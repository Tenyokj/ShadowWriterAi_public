from __future__ import annotations

from bot.database.db import Database


async def get_recent_channel_posts(
    db: Database,
    channel_id: int,
    limit: int = 12,
) -> list[str]:
    return await db.get_recent_channel_samples(channel_id=channel_id, limit=limit)
