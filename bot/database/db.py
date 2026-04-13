from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit

import aiosqlite
try:
    import asyncpg
except ImportError:  # pragma: no cover - optional until Postgres mode is enabled
    asyncpg = None

from bot.config import DB_PATH, settings


@dataclass(slots=True)
class PendingPost:
    id: int
    user_id: int
    channel_id: int
    idea: str
    text: str
    image_url: str | None = None
    image_source_url: str | None = None
    image_author: str | None = None
    image_query: str | None = None
    sticker_file_id: str | None = None
    custom_photo_file_id: str | None = None
    image_provider: str | None = None
    sources_json: str | None = None

    def has_sources(self) -> bool:
        if not self.sources_json:
            return False
        try:
            return bool(json.loads(self.sources_json))
        except json.JSONDecodeError:
            return False


@dataclass(slots=True)
class ChannelProfile:
    user_id: int
    channel_id: int
    channel_title: str | None = None
    channel_description: str | None = None
    channel_topic: str | None = None
    target_audience: str | None = None
    admin_persona: str | None = None
    content_pillars: str | None = None
    style_notes: str | None = None
    banned_topics: str | None = None


@dataclass(slots=True)
class AccessStatus:
    user_id: int
    free_posts_used: int = 0
    subscription_until: str | None = None
    last_free_generation_at: str | None = None

    def has_active_subscription(self) -> bool:
        if not self.subscription_until:
            return False
        return datetime.fromisoformat(self.subscription_until) > datetime.now(timezone.utc)

    def free_posts_left(self, limit: int) -> int:
        return max(limit - self.free_posts_used, 0)


@dataclass(slots=True)
class UserPreferences:
    user_id: int
    language_code: str = "en"


@dataclass(slots=True)
class StarPaymentRecord:
    id: int
    user_id: int
    plan_code: str
    amount: int
    currency: str
    telegram_payment_charge_id: str
    subscription_until: str
    refunded_at: str | None = None


@dataclass(slots=True)
class RuntimeSettings:
    free_posts_limit: int
    free_generation_cooldown_seconds: int
    max_unique_channels_free: int
    stars_price_14_days: int
    stars_price_30_days: int
    stars_price_90_days: int
    brand_animation_id: str
    brand_sticker_id: str
    about_text_ru: str
    about_text_en: str


@dataclass(slots=True)
class UserAISettings:
    user_id: int
    provider: str
    encrypted_api_key: str
    model_name: str
    is_active: bool
    created_at: str | None = None
    updated_at: str | None = None


@dataclass(slots=True)
class AbuseFlag:
    user_id: int
    is_suspicious: bool
    reason: str
    updated_at: str | None = None


@dataclass(slots=True)
class AnalyticsEvent:
    id: int
    user_id: int | None
    event_name: str
    meta: str | None
    created_at: str | None = None


class PostgresCursorWrapper:
    def __init__(
        self,
        rows: list[Any] | None = None,
        lastrowid: int | None = None,
    ) -> None:
        self._rows = rows or []
        self._index = 0
        self.lastrowid = lastrowid

    async def fetchone(self) -> Any | None:
        if self._index >= len(self._rows):
            return None
        row = self._rows[self._index]
        self._index += 1
        return row

    async def fetchall(self) -> list[Any]:
        rows = self._rows[self._index :]
        self._index = len(self._rows)
        return rows

    async def close(self) -> None:
        return None


class PostgresConnectionWrapper:
    def __init__(self, connection: Any) -> None:
        self._connection = connection

    async def execute(
        self,
        query: str,
        params: tuple[Any, ...] | list[Any] | None = None,
    ) -> PostgresCursorWrapper:
        adapted_query = self._adapt_query(query)
        values = tuple(params or ())
        normalized = query.lstrip().casefold()

        if normalized.startswith("select"):
            rows = await self._connection.fetch(adapted_query, *values)
            return PostgresCursorWrapper(rows=list(rows))

        if normalized.startswith("insert into pending_posts"):
            row = await self._connection.fetchrow(f"{adapted_query} RETURNING id", *values)
            lastrowid = int(row["id"]) if row is not None else None
            return PostgresCursorWrapper(lastrowid=lastrowid)

        await self._connection.execute(adapted_query, *values)
        return PostgresCursorWrapper()

    async def executescript(self, script: str) -> None:
        for statement in script.split(";"):
            trimmed = statement.strip()
            if trimmed:
                await self._connection.execute(trimmed)

    async def commit(self) -> None:
        return None

    async def close(self) -> None:
        await self._connection.close()

    @staticmethod
    def _adapt_query(query: str) -> str:
        index = 0
        parts: list[str] = []
        for char in query:
            if char == "?":
                index += 1
                parts.append(f"${index}")
            else:
                parts.append(char)
        return "".join(parts)


class Database:
    def __init__(
        self,
        db_path: str | None = None,
        database_url: str | None = None,
    ) -> None:
        self._db_path = db_path or str(DB_PATH)
        self._database_url = (database_url or settings.database_url or "").strip()
        self._backend = "postgres" if self._database_url else "sqlite"
        self._conn: aiosqlite.Connection | PostgresConnectionWrapper | None = None

    async def connect(self) -> None:
        if self._conn is None:
            if self._backend == "postgres":
                if asyncpg is None:
                    raise RuntimeError(
                        "DATABASE_URL задан, но зависимость asyncpg не установлена. "
                        "Установи зависимости заново через pip install -r requirements.txt."
                    )
                dsn = self._normalize_database_url(self._database_url)
                try:
                    connection = await asyncpg.connect(dsn)
                except ValueError as exc:
                    raise RuntimeError(
                        "Некорректный DATABASE_URL. Проверь, что ты заменил шаблон "
                        "[YOUR-PASSWORD] на реальный пароль и что пароль в URL закодирован."
                    ) from exc
                self._conn = PostgresConnectionWrapper(connection)
                return

            self._conn = await aiosqlite.connect(self._db_path)
            self._conn.row_factory = aiosqlite.Row

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    async def init(self) -> None:
        conn = self._require_conn()
        if self._backend == "postgres":
            await conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS user_channels (
                    user_id BIGINT PRIMARY KEY,
                    channel_id BIGINT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS pending_posts (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    channel_id BIGINT NOT NULL,
                    text TEXT NOT NULL,
                    image_url TEXT,
                    image_source_url TEXT,
                    image_author TEXT,
                    image_query TEXT,
                    sticker_file_id TEXT,
                    custom_photo_file_id TEXT,
                    image_provider TEXT,
                    sources_json TEXT,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS channel_profiles (
                    user_id BIGINT PRIMARY KEY,
                    channel_id BIGINT NOT NULL,
                    channel_title TEXT,
                    channel_description TEXT,
                    channel_topic TEXT,
                    target_audience TEXT,
                    admin_persona TEXT,
                    content_pillars TEXT,
                    style_notes TEXT,
                    banned_topics TEXT
                );

                CREATE TABLE IF NOT EXISTS user_access (
                    user_id BIGINT PRIMARY KEY,
                    free_posts_used INTEGER NOT NULL DEFAULT 0,
                    subscription_until TEXT,
                    last_free_generation_at TEXT
                );

                CREATE TABLE IF NOT EXISTS star_payments (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    plan_code TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    telegram_payment_charge_id TEXT NOT NULL,
                    subscription_until TEXT NOT NULL,
                    refunded_at TEXT,
                    paid_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id BIGINT PRIMARY KEY,
                    language_code TEXT NOT NULL DEFAULT 'en'
                );

                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS user_ai_settings (
                    user_id BIGINT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    encrypted_api_key TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS user_channel_history (
                    user_id BIGINT NOT NULL,
                    channel_id BIGINT NOT NULL,
                    first_connected_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    last_connected_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    connect_count INTEGER NOT NULL DEFAULT 1,
                    PRIMARY KEY (user_id, channel_id)
                );

                CREATE TABLE IF NOT EXISTS user_abuse_flags (
                    user_id BIGINT PRIMARY KEY,
                    is_suspicious INTEGER NOT NULL DEFAULT 1,
                    reason TEXT NOT NULL,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS analytics_events (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT,
                    event_name TEXT NOT NULL,
                    meta TEXT,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS channel_post_samples (
                    channel_id BIGINT NOT NULL,
                    message_id BIGINT NOT NULL,
                    text TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (channel_id, message_id)
                );
                """
            )
        else:
            await conn.executescript(
                """
            CREATE TABLE IF NOT EXISTS user_channels (
                user_id INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pending_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS channel_profiles (
                user_id INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL,
                channel_title TEXT,
                channel_description TEXT,
                channel_topic TEXT,
                target_audience TEXT,
                admin_persona TEXT,
                content_pillars TEXT,
                style_notes TEXT,
                banned_topics TEXT
            );

            CREATE TABLE IF NOT EXISTS user_access (
                user_id INTEGER PRIMARY KEY,
                free_posts_used INTEGER NOT NULL DEFAULT 0,
                subscription_until TEXT,
                last_free_generation_at TEXT
            );

            CREATE TABLE IF NOT EXISTS star_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan_code TEXT NOT NULL,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL,
                telegram_payment_charge_id TEXT NOT NULL,
                paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                subscription_until TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                language_code TEXT NOT NULL DEFAULT 'en'
            );

            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS user_ai_settings (
                user_id INTEGER PRIMARY KEY,
                provider TEXT NOT NULL,
                encrypted_api_key TEXT NOT NULL,
                model_name TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS user_channel_history (
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                first_connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                connect_count INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (user_id, channel_id)
            );

            CREATE TABLE IF NOT EXISTS user_abuse_flags (
                user_id INTEGER PRIMARY KEY,
                is_suspicious INTEGER NOT NULL DEFAULT 1,
                reason TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS analytics_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event_name TEXT NOT NULL,
                meta TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS channel_post_samples (
                channel_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (channel_id, message_id)
            );
            """
            )
        await self._ensure_pending_post_columns()
        await self._ensure_star_payment_columns()
        await self._ensure_user_access_columns()
        await conn.commit()

    async def set_user_channel(self, user_id: int, channel_id: int) -> None:
        conn = self._require_conn()
        await conn.execute(
            """
            INSERT INTO user_channels (user_id, channel_id)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET channel_id = excluded.channel_id
            """,
            (user_id, channel_id),
        )
        await conn.commit()

    async def record_user_channel_history(self, user_id: int, channel_id: int) -> None:
        conn = self._require_conn()
        now = self._timestamp_value()
        await conn.execute(
            """
            INSERT INTO user_channel_history (
                user_id, channel_id, first_connected_at, last_connected_at, connect_count
            )
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(user_id, channel_id) DO UPDATE SET
                last_connected_at = excluded.last_connected_at,
                connect_count = user_channel_history.connect_count + 1
            """,
            (user_id, channel_id, now, now),
        )
        await conn.commit()

    async def has_user_connected_channel_before(self, user_id: int, channel_id: int) -> bool:
        conn = self._require_conn()
        cursor = await conn.execute(
            """
            SELECT 1
            FROM user_channel_history
            WHERE user_id = ? AND channel_id = ?
            LIMIT 1
            """,
            (user_id, channel_id),
        )
        row = await cursor.fetchone()
        await cursor.close()
        return row is not None

    async def count_user_unique_channels(self, user_id: int) -> int:
        conn = self._require_conn()
        cursor = await conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM user_channel_history
            WHERE user_id = ?
            """,
            (user_id,),
        )
        row = await cursor.fetchone()
        await cursor.close()
        return int(row["total"]) if row is not None else 0

    async def add_channel_post_sample(
        self,
        channel_id: int,
        message_id: int,
        text: str,
    ) -> None:
        conn = self._require_conn()
        await conn.execute(
            """
            INSERT INTO channel_post_samples (channel_id, message_id, text, created_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(channel_id, message_id) DO UPDATE SET
                text = excluded.text,
                created_at = CURRENT_TIMESTAMP
            """,
            (channel_id, message_id, text),
        )
        await conn.execute(
            """
            DELETE FROM channel_post_samples
            WHERE channel_id = ?
              AND message_id NOT IN (
                  SELECT message_id
                  FROM channel_post_samples
                  WHERE channel_id = ?
                  ORDER BY created_at DESC, message_id DESC
                  LIMIT 50
              )
            """,
            (channel_id, channel_id),
        )
        await conn.commit()

    async def get_recent_channel_samples(self, channel_id: int, limit: int = 12) -> list[str]:
        conn = self._require_conn()
        cursor = await conn.execute(
            """
            SELECT text
            FROM channel_post_samples
            WHERE channel_id = ?
            ORDER BY created_at DESC, message_id DESC
            LIMIT ?
            """,
            (channel_id, limit),
        )
        rows = await cursor.fetchall()
        await cursor.close()
        return [str(row["text"]) for row in rows]

    async def mark_user_suspicious(self, user_id: int, reason: str) -> None:
        conn = self._require_conn()
        now = self._timestamp_value()
        await conn.execute(
            """
            INSERT INTO user_abuse_flags (user_id, is_suspicious, reason, updated_at)
            VALUES (?, 1, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                is_suspicious = 1,
                reason = excluded.reason,
                updated_at = excluded.updated_at
            """,
            (user_id, reason, now),
        )
        await conn.commit()
        await self.track_event(
            event_name="user_flagged_suspicious",
            user_id=user_id,
            meta=reason,
        )

    async def get_abuse_flag(self, user_id: int) -> AbuseFlag | None:
        conn = self._require_conn()
        cursor = await conn.execute(
            """
            SELECT user_id, is_suspicious, reason, updated_at
            FROM user_abuse_flags
            WHERE user_id = ?
            """,
            (user_id,),
        )
        row = await cursor.fetchone()
        await cursor.close()
        if row is None:
            return None
        return AbuseFlag(
            user_id=int(row["user_id"]),
            is_suspicious=bool(int(row["is_suspicious"])),
            reason=str(row["reason"]),
            updated_at=row["updated_at"],
        )

    async def count_suspicious_users(self) -> int:
        conn = self._require_conn()
        cursor = await conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM user_abuse_flags
            WHERE is_suspicious = 1
            """
        )
        row = await cursor.fetchone()
        await cursor.close()
        return int(row["total"]) if row is not None else 0

    async def get_recent_suspicious_users(self, limit: int = 3) -> list[AbuseFlag]:
        conn = self._require_conn()
        cursor = await conn.execute(
            """
            SELECT user_id, is_suspicious, reason, updated_at
            FROM user_abuse_flags
            WHERE is_suspicious = 1
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = await cursor.fetchall()
        await cursor.close()
        return [
            AbuseFlag(
                user_id=int(row["user_id"]),
                is_suspicious=bool(int(row["is_suspicious"])),
                reason=str(row["reason"]),
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    async def track_event(
        self,
        event_name: str,
        user_id: int | None = None,
        meta: str | None = None,
    ) -> None:
        conn = self._require_conn()
        await conn.execute(
            """
            INSERT INTO analytics_events (user_id, event_name, meta)
            VALUES (?, ?, ?)
            """,
            (user_id, event_name, meta),
        )
        await conn.commit()

    async def count_events(self, event_name: str) -> int:
        conn = self._require_conn()
        cursor = await conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM analytics_events
            WHERE event_name = ?
            """,
            (event_name,),
        )
        row = await cursor.fetchone()
        await cursor.close()
        return int(row["total"]) if row is not None else 0

    async def get_analytics_summary(self) -> dict[str, int]:
        keys = [
            "start_command",
            "ai_opened",
            "ai_connected",
            "ai_validation_failed",
            "channel_connected",
            "connect_rejected_limit",
            "post_attempt",
            "post_rejected_fact_request",
            "post_success",
            "post_failed_no_ai",
            "post_failed_groq",
            "payment_success",
            "user_flagged_suspicious",
            "unhandled_error",
        ]
        return {key: await self.count_events(key) for key in keys}

    async def replace_channel_profile(
        self,
        user_id: int,
        channel_id: int,
        channel_title: str | None = None,
        channel_description: str | None = None,
    ) -> None:
        conn = self._require_conn()
        await conn.execute(
            """
            INSERT INTO channel_profiles (
                user_id, channel_id, channel_title, channel_description, channel_topic,
                target_audience, admin_persona, content_pillars, style_notes, banned_topics
            )
            VALUES (?, ?, ?, ?, NULL, NULL, NULL, NULL, NULL, NULL)
            ON CONFLICT(user_id) DO UPDATE SET
                channel_id = excluded.channel_id,
                channel_title = excluded.channel_title,
                channel_description = excluded.channel_description,
                channel_topic = NULL,
                target_audience = NULL,
                admin_persona = NULL,
                content_pillars = NULL,
                style_notes = NULL,
                banned_topics = NULL
            """,
            (user_id, channel_id, channel_title, channel_description),
        )
        await conn.commit()

    async def upsert_channel_profile(
        self,
        user_id: int,
        channel_id: int,
        channel_title: str | None = None,
        channel_description: str | None = None,
        channel_topic: str | None = None,
        target_audience: str | None = None,
        admin_persona: str | None = None,
        content_pillars: str | None = None,
        style_notes: str | None = None,
        banned_topics: str | None = None,
    ) -> None:
        conn = self._require_conn()
        existing = await self.get_channel_profile(user_id)
        if existing is None:
            await conn.execute(
                """
                INSERT INTO channel_profiles (
                    user_id, channel_id, channel_title, channel_description, channel_topic,
                    target_audience, admin_persona, content_pillars, style_notes, banned_topics
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    channel_id,
                    channel_title,
                    channel_description,
                    channel_topic,
                    target_audience,
                    admin_persona,
                    content_pillars,
                    style_notes,
                    banned_topics,
                ),
            )
        else:
            await conn.execute(
                """
                UPDATE channel_profiles
                SET channel_id = ?,
                    channel_title = COALESCE(?, channel_title),
                    channel_description = COALESCE(?, channel_description),
                    channel_topic = COALESCE(?, channel_topic),
                    target_audience = COALESCE(?, target_audience),
                    admin_persona = COALESCE(?, admin_persona),
                    content_pillars = COALESCE(?, content_pillars),
                    style_notes = COALESCE(?, style_notes),
                    banned_topics = COALESCE(?, banned_topics)
                WHERE user_id = ?
                """,
                (
                    channel_id,
                    channel_title,
                    channel_description,
                    channel_topic,
                    target_audience,
                    admin_persona,
                    content_pillars,
                    style_notes,
                    banned_topics,
                    user_id,
                ),
            )
        await conn.commit()

    async def get_channel_profile(self, user_id: int) -> ChannelProfile | None:
        conn = self._require_conn()
        cursor = await conn.execute(
            """
            SELECT user_id, channel_id, channel_title, channel_description, channel_topic,
                   target_audience, admin_persona, content_pillars, style_notes, banned_topics
            FROM channel_profiles
            WHERE user_id = ?
            """,
            (user_id,),
        )
        row = await cursor.fetchone()
        await cursor.close()
        if row is None:
            return None

        return ChannelProfile(
            user_id=int(row["user_id"]),
            channel_id=int(row["channel_id"]),
            channel_title=row["channel_title"],
            channel_description=row["channel_description"],
            channel_topic=row["channel_topic"],
            target_audience=row["target_audience"],
            admin_persona=row["admin_persona"],
            content_pillars=row["content_pillars"],
            style_notes=row["style_notes"],
            banned_topics=row["banned_topics"],
        )

    async def get_user_channel(self, user_id: int) -> int | None:
        conn = self._require_conn()
        cursor = await conn.execute(
            "SELECT channel_id FROM user_channels WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
        await cursor.close()
        if row is None:
            return None
        return int(row["channel_id"])

    async def create_pending_post(
        self,
        user_id: int,
        channel_id: int,
        idea: str,
        text: str,
        image_url: str | None = None,
        image_source_url: str | None = None,
        image_author: str | None = None,
        image_query: str | None = None,
        sticker_file_id: str | None = None,
        custom_photo_file_id: str | None = None,
        image_provider: str | None = None,
        sources_json: str | None = None,
    ) -> PendingPost:
        conn = self._require_conn()
        cursor = await conn.execute(
            """
            INSERT INTO pending_posts (
                user_id,
                channel_id,
                idea,
                text,
                image_url,
                image_source_url,
                image_author,
                image_query,
                sticker_file_id,
                custom_photo_file_id,
                image_provider,
                sources_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                channel_id,
                idea,
                text,
                image_url,
                image_source_url,
                image_author,
                image_query,
                sticker_file_id,
                custom_photo_file_id,
                image_provider,
                sources_json,
            ),
        )
        await conn.commit()
        pending_id = cursor.lastrowid
        await cursor.close()
        return PendingPost(
            id=pending_id,
            user_id=user_id,
            channel_id=channel_id,
            idea=idea,
            text=text,
            image_url=image_url,
            image_source_url=image_source_url,
            image_author=image_author,
            image_query=image_query,
            sticker_file_id=sticker_file_id,
            custom_photo_file_id=custom_photo_file_id,
            image_provider=image_provider,
            sources_json=sources_json,
        )

    async def get_pending_post(self, pending_post_id: int) -> PendingPost | None:
        conn = self._require_conn()
        cursor = await conn.execute(
            """
            SELECT id, user_id, channel_id, text, image_url, image_source_url,
                   idea, image_author, image_query, sticker_file_id, custom_photo_file_id,
                   image_provider, sources_json
            FROM pending_posts
            WHERE id = ?
            """,
            (pending_post_id,),
        )
        row = await cursor.fetchone()
        await cursor.close()
        if row is None:
            return None
        return PendingPost(
            id=int(row["id"]),
            user_id=int(row["user_id"]),
            channel_id=int(row["channel_id"]),
            idea=str(row["idea"] or ""),
            text=str(row["text"]),
            image_url=row["image_url"],
            image_source_url=row["image_source_url"],
            image_author=row["image_author"],
            image_query=row["image_query"],
            sticker_file_id=row["sticker_file_id"],
            custom_photo_file_id=row["custom_photo_file_id"],
            image_provider=row["image_provider"],
            sources_json=row["sources_json"],
        )

    async def delete_pending_post(self, pending_post_id: int) -> None:
        conn = self._require_conn()
        await conn.execute(
            "DELETE FROM pending_posts WHERE id = ?",
            (pending_post_id,),
        )
        await conn.commit()

    async def delete_pending_posts_for_user(self, user_id: int) -> None:
        conn = self._require_conn()
        await conn.execute(
            "DELETE FROM pending_posts WHERE user_id = ?",
            (user_id,),
        )
        await conn.commit()

    async def update_pending_post_photo(
        self,
        pending_post_id: int,
        image_url: str | None = None,
        image_source_url: str | None = None,
        image_author: str | None = None,
        image_provider: str | None = None,
        custom_photo_file_id: str | None = None,
    ) -> None:
        conn = self._require_conn()
        await conn.execute(
            """
            UPDATE pending_posts
            SET image_url = ?,
                image_source_url = ?,
                image_author = ?,
                image_provider = ?,
                custom_photo_file_id = ?
            WHERE id = ?
            """,
            (
                image_url,
                image_source_url,
                image_author,
                image_provider,
                custom_photo_file_id,
                pending_post_id,
            ),
        )
        await conn.commit()

    async def update_pending_post_text(
        self,
        pending_post_id: int,
        text: str,
    ) -> None:
        conn = self._require_conn()
        await conn.execute(
            """
            UPDATE pending_posts
            SET text = ?
            WHERE id = ?
            """,
            (text, pending_post_id),
        )
        await conn.commit()

    async def update_pending_post_meta(
        self,
        pending_post_id: int,
        image_query: str | None = None,
        sticker_file_id: str | None = None,
        sources_json: str | None = None,
    ) -> None:
        conn = self._require_conn()
        await conn.execute(
            """
            UPDATE pending_posts
            SET image_query = ?,
                sticker_file_id = ?,
                sources_json = ?
            WHERE id = ?
            """,
            (image_query, sticker_file_id, sources_json, pending_post_id),
        )
        await conn.commit()

    async def set_pending_post_custom_photo(
        self,
        pending_post_id: int,
        custom_photo_file_id: str,
    ) -> None:
        conn = self._require_conn()
        await conn.execute(
            """
            UPDATE pending_posts
            SET custom_photo_file_id = ?
            WHERE id = ?
            """,
            (custom_photo_file_id, pending_post_id),
        )
        await conn.commit()

    async def get_access_status(self, user_id: int) -> AccessStatus:
        conn = self._require_conn()
        cursor = await conn.execute(
            """
            SELECT user_id, free_posts_used, subscription_until, last_free_generation_at
            FROM user_access
            WHERE user_id = ?
            """,
            (user_id,),
        )
        row = await cursor.fetchone()
        await cursor.close()
        if row is None:
            await conn.execute(
                """
                INSERT INTO user_access (user_id, free_posts_used, subscription_until, last_free_generation_at)
                VALUES (?, 0, NULL, NULL)
                """,
                (user_id,),
            )
            await conn.commit()
            return AccessStatus(user_id=user_id)

        return AccessStatus(
            user_id=int(row["user_id"]),
            free_posts_used=int(row["free_posts_used"]),
            subscription_until=row["subscription_until"],
            last_free_generation_at=row["last_free_generation_at"],
        )

    async def increment_free_posts_used(self, user_id: int) -> None:
        conn = self._require_conn()
        await self.get_access_status(user_id)
        now = datetime.now(timezone.utc).isoformat()
        await conn.execute(
            """
            UPDATE user_access
            SET free_posts_used = free_posts_used + 1,
                last_free_generation_at = ?
            WHERE user_id = ?
            """,
            (now, user_id),
        )
        await conn.commit()

    async def get_user_preferences(self, user_id: int) -> UserPreferences:
        conn = self._require_conn()
        cursor = await conn.execute(
            """
            SELECT user_id, language_code
            FROM user_preferences
            WHERE user_id = ?
            """,
            (user_id,),
        )
        row = await cursor.fetchone()
        await cursor.close()
        if row is None:
            await conn.execute(
                """
                INSERT INTO user_preferences (user_id, language_code)
                VALUES (?, 'en')
                """,
                (user_id,),
            )
            await conn.commit()
            return UserPreferences(user_id=user_id, language_code="en")

        return UserPreferences(
            user_id=int(row["user_id"]),
            language_code=str(row["language_code"]),
        )

    async def set_user_language(self, user_id: int, language_code: str) -> None:
        conn = self._require_conn()
        await conn.execute(
            """
            INSERT INTO user_preferences (user_id, language_code)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET language_code = excluded.language_code
            """,
            (user_id, language_code),
        )
        await conn.commit()

    async def get_runtime_settings(self) -> RuntimeSettings:
        conn = self._require_conn()
        cursor = await conn.execute(
            """
            SELECT key, value
            FROM app_settings
            """
        )
        rows = await cursor.fetchall()
        await cursor.close()
        values = {str(row["key"]): str(row["value"]) for row in rows}

        return RuntimeSettings(
            free_posts_limit=self._int_setting(values, "free_posts_limit", settings.free_posts_limit),
            free_generation_cooldown_seconds=self._int_setting(
                values,
                "free_generation_cooldown_seconds",
                settings.free_generation_cooldown_seconds,
            ),
            max_unique_channels_free=self._int_setting(
                values,
                "max_unique_channels_free",
                settings.max_unique_channels_free,
            ),
            stars_price_14_days=self._int_setting(
                values,
                "stars_price_14_days",
                settings.stars_price_14_days,
            ),
            stars_price_30_days=self._int_setting(
                values,
                "stars_price_30_days",
                settings.stars_price_30_days,
            ),
            stars_price_90_days=self._int_setting(
                values,
                "stars_price_90_days",
                settings.stars_price_90_days,
            ),
            brand_animation_id=values.get("brand_animation_id", settings.brand_animation_id),
            brand_sticker_id=values.get("brand_sticker_id", settings.brand_sticker_id),
            about_text_ru=values.get("about_text_ru", ""),
            about_text_en=values.get("about_text_en", ""),
        )

    async def set_runtime_setting(self, key: str, value: str) -> None:
        conn = self._require_conn()
        await conn.execute(
            """
            INSERT INTO app_settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )
        await conn.commit()

    async def upsert_user_ai_settings(
        self,
        user_id: int,
        provider: str,
        encrypted_api_key: str,
        model_name: str,
        is_active: bool = True,
    ) -> None:
        conn = self._require_conn()
        now = self._timestamp_value()
        await conn.execute(
            """
            INSERT INTO user_ai_settings (
                user_id, provider, encrypted_api_key, model_name, is_active, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                provider = excluded.provider,
                encrypted_api_key = excluded.encrypted_api_key,
                model_name = excluded.model_name,
                is_active = excluded.is_active,
                updated_at = excluded.updated_at
            """,
            (
                user_id,
                provider,
                encrypted_api_key,
                model_name,
                1 if is_active else 0,
                now,
                now,
            ),
        )
        await conn.commit()

    async def get_user_ai_settings(self, user_id: int) -> UserAISettings | None:
        conn = self._require_conn()
        cursor = await conn.execute(
            """
            SELECT user_id, provider, encrypted_api_key, model_name, is_active, created_at, updated_at
            FROM user_ai_settings
            WHERE user_id = ?
            """,
            (user_id,),
        )
        row = await cursor.fetchone()
        await cursor.close()
        if row is None:
            return None
        return UserAISettings(
            user_id=int(row["user_id"]),
            provider=str(row["provider"]),
            encrypted_api_key=str(row["encrypted_api_key"]),
            model_name=str(row["model_name"]),
            is_active=bool(int(row["is_active"])),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def delete_user_ai_settings(self, user_id: int) -> None:
        conn = self._require_conn()
        await conn.execute(
            "DELETE FROM user_ai_settings WHERE user_id = ?",
            (user_id,),
        )
        await conn.commit()

    async def full_reset_user_workspace(self, user_id: int) -> None:
        conn = self._require_conn()
        await conn.execute("DELETE FROM user_channels WHERE user_id = ?", (user_id,))
        await conn.execute("DELETE FROM channel_profiles WHERE user_id = ?", (user_id,))
        await conn.execute("DELETE FROM pending_posts WHERE user_id = ?", (user_id,))
        await conn.execute("DELETE FROM user_ai_settings WHERE user_id = ?", (user_id,))
        await conn.commit()

    async def activate_subscription(
        self,
        user_id: int,
        duration_minutes: int,
        plan_code: str,
        amount: int,
        currency: str,
        telegram_payment_charge_id: str,
    ) -> str:
        conn = self._require_conn()
        access = await self.get_access_status(user_id)
        now = datetime.now(timezone.utc)

        if access.subscription_until:
            current_expiry = datetime.fromisoformat(access.subscription_until)
            start_at = current_expiry if current_expiry > now else now
        else:
            start_at = now

        expires_at = start_at + timedelta(minutes=duration_minutes)
        expires_iso = expires_at.isoformat()

        await conn.execute(
            """
            UPDATE user_access
            SET subscription_until = ?
            WHERE user_id = ?
            """,
            (expires_iso, user_id),
        )
        await conn.execute(
            """
            INSERT INTO star_payments (
                user_id, plan_code, amount, currency, telegram_payment_charge_id, subscription_until
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                plan_code,
                amount,
                currency,
                telegram_payment_charge_id,
                expires_iso,
            ),
        )
        await conn.commit()
        return expires_iso

    async def get_last_unrefunded_test_payment(
        self,
        user_id: int,
    ) -> StarPaymentRecord | None:
        conn = self._require_conn()
        cursor = await conn.execute(
            """
            SELECT id, user_id, plan_code, amount, currency,
                   telegram_payment_charge_id, subscription_until, refunded_at
            FROM star_payments
            WHERE user_id = ?
              AND plan_code = 'sub_test_5m'
              AND refunded_at IS NULL
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,),
        )
        row = await cursor.fetchone()
        await cursor.close()
        if row is None:
            return None

        return StarPaymentRecord(
            id=int(row["id"]),
            user_id=int(row["user_id"]),
            plan_code=str(row["plan_code"]),
            amount=int(row["amount"]),
            currency=str(row["currency"]),
            telegram_payment_charge_id=str(row["telegram_payment_charge_id"]),
            subscription_until=str(row["subscription_until"]),
            refunded_at=row["refunded_at"],
        )

    async def mark_star_payment_refunded(self, payment_id: int) -> None:
        conn = self._require_conn()
        refunded_at = datetime.now(timezone.utc).isoformat()
        await conn.execute(
            """
            UPDATE star_payments
            SET refunded_at = ?
            WHERE id = ?
            """,
            (refunded_at, payment_id),
        )
        await conn.commit()

    async def revoke_test_subscription_if_recent(self, user_id: int) -> None:
        conn = self._require_conn()
        access = await self.get_access_status(user_id)
        if not access.subscription_until:
            return

        expires_at = datetime.fromisoformat(access.subscription_until)
        now = datetime.now(timezone.utc)
        # If a very short-lived test subscription is still fresh, revoke it carefully.
        if expires_at > now and expires_at <= now + timedelta(minutes=10):
            await conn.execute(
                """
                UPDATE user_access
                SET subscription_until = ?
                WHERE user_id = ?
                """,
                (now.isoformat(), user_id),
            )
            await conn.commit()

    def _require_conn(self) -> aiosqlite.Connection | PostgresConnectionWrapper:
        if self._conn is None:
            raise RuntimeError("Database connection is not initialized")
        return self._conn

    async def _ensure_pending_post_columns(self) -> None:
        conn = self._require_conn()
        if self._backend == "postgres":
            await conn.execute(
                "ALTER TABLE pending_posts ADD COLUMN IF NOT EXISTS image_url TEXT"
            )
            await conn.execute(
                "ALTER TABLE pending_posts ADD COLUMN IF NOT EXISTS idea TEXT"
            )
            await conn.execute(
                "ALTER TABLE pending_posts ADD COLUMN IF NOT EXISTS image_source_url TEXT"
            )
            await conn.execute(
                "ALTER TABLE pending_posts ADD COLUMN IF NOT EXISTS image_author TEXT"
            )
            await conn.execute(
                "ALTER TABLE pending_posts ADD COLUMN IF NOT EXISTS image_query TEXT"
            )
            await conn.execute(
                "ALTER TABLE pending_posts ADD COLUMN IF NOT EXISTS sticker_file_id TEXT"
            )
            await conn.execute(
                "ALTER TABLE pending_posts ADD COLUMN IF NOT EXISTS custom_photo_file_id TEXT"
            )
            await conn.execute(
                "ALTER TABLE pending_posts ADD COLUMN IF NOT EXISTS image_provider TEXT"
            )
            await conn.execute(
                "ALTER TABLE pending_posts ADD COLUMN IF NOT EXISTS sources_json TEXT"
            )
            return

        cursor = await conn.execute("PRAGMA table_info(pending_posts)")
        rows = await cursor.fetchall()
        await cursor.close()

        existing_columns = {row["name"] for row in rows}
        required_columns = {
            "idea": "TEXT",
            "image_url": "TEXT",
            "image_source_url": "TEXT",
            "image_author": "TEXT",
            "image_query": "TEXT",
            "sticker_file_id": "TEXT",
            "custom_photo_file_id": "TEXT",
            "image_provider": "TEXT",
            "sources_json": "TEXT",
        }

        for column_name, column_type in required_columns.items():
            if column_name not in existing_columns:
                await conn.execute(
                    f"ALTER TABLE pending_posts ADD COLUMN {column_name} {column_type}"
                )

    async def _ensure_star_payment_columns(self) -> None:
        conn = self._require_conn()
        if self._backend == "postgres":
            await conn.execute(
                "ALTER TABLE star_payments ADD COLUMN IF NOT EXISTS refunded_at TEXT"
            )
            return

        cursor = await conn.execute("PRAGMA table_info(star_payments)")
        rows = await cursor.fetchall()
        await cursor.close()

        existing_columns = {row["name"] for row in rows}
        required_columns = {
            "refunded_at": "TEXT",
        }

        for column_name, column_type in required_columns.items():
            if column_name not in existing_columns:
                await conn.execute(
                    f"ALTER TABLE star_payments ADD COLUMN {column_name} {column_type}"
                )

    async def _ensure_user_access_columns(self) -> None:
        conn = self._require_conn()
        if self._backend == "postgres":
            await conn.execute(
                "ALTER TABLE user_access ADD COLUMN IF NOT EXISTS last_free_generation_at TEXT"
            )
            return

        cursor = await conn.execute("PRAGMA table_info(user_access)")
        rows = await cursor.fetchall()
        await cursor.close()

        existing_columns = {row["name"] for row in rows}
        required_columns = {
            "last_free_generation_at": "TEXT",
        }

        for column_name, column_type in required_columns.items():
            if column_name not in existing_columns:
                await conn.execute(
                    f"ALTER TABLE user_access ADD COLUMN {column_name} {column_type}"
                )

    @staticmethod
    def _int_setting(values: dict[str, str], key: str, default: int) -> int:
        raw_value = values.get(key)
        if raw_value is None:
            return default
        try:
            return int(raw_value)
        except ValueError:
            return default

    def _timestamp_value(self) -> datetime | str:
        now = datetime.now(timezone.utc)
        if self._backend == "postgres":
            return now
        return now.isoformat()

    @staticmethod
    def _normalize_database_url(database_url: str) -> str:
        if "[YOUR-PASSWORD]" in database_url or "YOUR-PASSWORD" in database_url:
            raise RuntimeError(
                "DATABASE_URL всё ещё содержит шаблонный пароль. "
                "Открой Supabase -> Connect и подставь свой реальный database password."
            )

        parsed = urlsplit(database_url)
        if parsed.username is None and parsed.hostname and parsed.hostname.startswith("postgres."):
            raise RuntimeError(
                "DATABASE_URL выглядит некорректно: пароль, скорее всего, содержит спецсимволы "
                "вроде /, @, :, # или ?. В строке подключения такой пароль нужно URL-кодировать. "
                "Скопируй заново Session pooler string из Supabase Connect или закодируй пароль перед вставкой."
            )
        if not parsed.username or parsed.password is None:
            return database_url

        raw_user = parsed.username
        raw_password = parsed.password
        host = parsed.hostname or ""
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"

        auth = f"{quote(raw_user, safe='')}:{quote(raw_password, safe='')}"
        if parsed.port:
            netloc = f"{auth}@{host}:{parsed.port}"
        else:
            netloc = f"{auth}@{host}"

        return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))
