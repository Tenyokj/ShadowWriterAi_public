from __future__ import annotations

import html

import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.config import DEFAULT_MASTER_ENCRYPTION_KEY, settings
from bot.database.db import Database
from bot.i18n import t
from bot.services.groq_ai import GroqAIService
from bot.services.secret_box import SecretBox


router = Router()


class AISettingsState(StatesGroup):
    waiting_for_groq_key = State()


@router.message(Command("ai"))
async def ai_command(
    message: Message,
    state: FSMContext,
    db: Database,
    secret_box: SecretBox,
) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    await db.track_event("ai_opened", user_id=message.from_user.id)
    if not secret_box.is_configured:
        await message.answer(t(language, "ai_storage_not_ready"))
        return

    await state.clear()
    await state.set_state(AISettingsState.waiting_for_groq_key)
    await state.update_data(language=language)
    await message.answer(
        t(language, "ai_intro", model=html.escape(settings.groq_model))
    )


@router.message(Command("groq_help"))
async def groq_help_command(message: Message, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    if settings.groq_tutorial_video_id:
        await message.answer_video(settings.groq_tutorial_video_id)
    await message.answer(t(language, "groq_help_message"))


@router.message(Command("ai_status"))
async def ai_status_command(message: Message, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    ai_settings = await db.get_user_ai_settings(message.from_user.id)
    if ai_settings is None or not ai_settings.is_active:
        await message.answer(
            t(language, "ai_status_empty", model=html.escape(settings.groq_model))
        )
        return

    await message.answer(
        t(
            language,
            "ai_status_connected",
            provider=html.escape(ai_settings.provider),
            model=html.escape(ai_settings.model_name),
        )
    )


@router.message(Command("ai_disconnect"))
async def ai_disconnect_command(message: Message, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    await db.delete_user_ai_settings(message.from_user.id)
    await message.answer(t(language, "ai_disconnected"))


@router.message(AISettingsState.waiting_for_groq_key)
async def receive_groq_key(
    message: Message,
    state: FSMContext,
    db: Database,
    groq_service: GroqAIService,
    secret_box: SecretBox,
) -> None:
    data = await state.get_data()
    language = data.get("language", "ru")
    api_key = (message.text or "").strip()

    if not api_key:
        await message.answer(t(language, "ai_key_invalid"))
        return
    if api_key.startswith("/"):
        await message.answer(t(language, "ai_key_invalid"))
        return
    if not secret_box.is_configured:
        await state.clear()
        await message.answer(t(language, "ai_storage_not_ready"))
        return

    await message.answer(t(language, "ai_validating"))
    try:
        await groq_service.validate_api_key(api_key)
    except httpx.HTTPStatusError as exc:
        await db.track_event("ai_validation_failed", user_id=message.from_user.id, meta=str(exc))
        await message.answer(
            t(language, "ai_key_check_failed", error=html.escape(str(exc)))
        )
        return
    except Exception as exc:
        await db.track_event("ai_validation_failed", user_id=message.from_user.id, meta=str(exc))
        await message.answer(
            t(language, "ai_key_check_failed", error=html.escape(str(exc)))
        )
        return

    encrypted_key = secret_box.encrypt(api_key)
    await db.upsert_user_ai_settings(
        user_id=message.from_user.id,
        provider="groq",
        encrypted_api_key=encrypted_key,
        model_name=settings.groq_model,
        is_active=True,
    )
    await db.track_event("ai_connected", user_id=message.from_user.id)
    await state.clear()
    await message.answer(
        t(language, "ai_connected", model=html.escape(settings.groq_model))
    )
