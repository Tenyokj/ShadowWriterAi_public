from __future__ import annotations

import html
import logging

from aiogram import Router
from aiogram.types import CallbackQuery, ErrorEvent, Message

from bot.config import settings
from bot.database.db import Database
from bot.i18n import t


router = Router()
logger = logging.getLogger(__name__)


def _extract_message(event: ErrorEvent) -> Message | None:
    update = event.update
    return getattr(update, "message", None)


def _extract_callback(event: ErrorEvent) -> CallbackQuery | None:
    update = event.update
    return getattr(update, "callback_query", None)


@router.errors()
async def global_error_handler(event: ErrorEvent, db: Database) -> bool:
    message = _extract_message(event)
    callback = _extract_callback(event)
    user_id = None
    language = "ru"

    try:
        if message and message.from_user:
            user_id = message.from_user.id
            language = (await db.get_user_preferences(user_id)).language_code
        elif callback and callback.from_user:
            user_id = callback.from_user.id
            language = (await db.get_user_preferences(user_id)).language_code
    except Exception:
        pass

    logger.error("Unhandled bot error", exc_info=event.exception)
    try:
        await db.track_event(
            "unhandled_error",
            user_id=user_id,
            meta=repr(event.exception),
        )
    except Exception:
        logger.exception("Failed to write unhandled_error analytics")

    try:
        if message:
            if settings.app_env == "dev":
                await message.answer(
                    f"{t(language, 'error_generic_message')}\n\n"
                    f"<code>{html.escape(repr(event.exception))}</code>"
                )
            else:
                await message.answer(t(language, "error_generic_message"))
        elif callback:
            if settings.app_env == "dev":
                await callback.answer(
                    f"{t(language, 'error_generic_callback')}\n{repr(event.exception)}",
                    show_alert=True,
                )
            else:
                await callback.answer(t(language, "error_generic_callback"), show_alert=True)
    except Exception:
        logger.exception("Failed to send fallback error message")

    return True
