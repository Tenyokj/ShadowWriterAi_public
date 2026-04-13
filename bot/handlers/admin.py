from __future__ import annotations

import html

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.config import settings
from bot.database.db import Database, RuntimeSettings
from bot.i18n import t
from bot.keyboards.admin import admin_panel_keyboard


router = Router()


class AdminState(StatesGroup):
    waiting_for_value = State()


def _is_admin(user_id: int) -> bool:
    return settings.admin_user_id > 0 and user_id == settings.admin_user_id


def _setting_label(language: str, key: str) -> str:
    labels = {
        "free_posts_limit": t(language, "admin_free_limit_button"),
        "free_generation_cooldown_seconds": t(language, "admin_cooldown_button"),
        "max_unique_channels_free": t(language, "admin_unique_channels_button"),
        "stars_price_14_days": t(language, "admin_price_14_button"),
        "stars_price_30_days": t(language, "admin_price_30_button"),
        "stars_price_90_days": t(language, "admin_price_90_button"),
        "brand_animation_id": t(language, "admin_animation_button"),
        "brand_sticker_id": t(language, "admin_sticker_button"),
        "about_text_ru": t(language, "admin_about_ru_button"),
        "about_text_en": t(language, "admin_about_en_button"),
    }
    return labels[key]


def _format_recent_flags(flags: list, language: str) -> str:
    if not flags:
        return t(language, "admin_flags_empty")
    return "\n".join(
        t(
            language,
            "admin_flag_line",
            user_id=flag.user_id,
            reason=html.escape(flag.reason),
        )
        for flag in flags
    )


def _admin_summary(
    language: str,
    runtime: RuntimeSettings,
    suspicious_total: int,
    recent_flags: list,
    analytics: dict[str, int],
) -> str:
    about_ru_state = t(language, "admin_value_set") if runtime.about_text_ru else t(language, "admin_value_empty")
    about_en_state = t(language, "admin_value_set") if runtime.about_text_en else t(language, "admin_value_empty")
    gif_state = runtime.brand_animation_id or "—"
    sticker_state = runtime.brand_sticker_id or "—"
    return t(
        language,
        "admin_panel_message",
        free_limit=runtime.free_posts_limit,
        cooldown=runtime.free_generation_cooldown_seconds,
        unique_channels=runtime.max_unique_channels_free,
        price_14=runtime.stars_price_14_days,
        price_30=runtime.stars_price_30_days,
        price_90=runtime.stars_price_90_days,
        animation_id=html.escape(gif_state),
        sticker_id=html.escape(sticker_state),
        about_ru=about_ru_state,
        about_en=about_en_state,
        suspicious_total=suspicious_total,
        recent_flags=_format_recent_flags(recent_flags, language),
        start_total=analytics.get("start_command", 0),
        ai_opened=analytics.get("ai_opened", 0),
        ai_connected=analytics.get("ai_connected", 0),
        ai_failed=analytics.get("ai_validation_failed", 0),
        channel_connected=analytics.get("channel_connected", 0),
        connect_rejected=analytics.get("connect_rejected_limit", 0),
        post_attempt=analytics.get("post_attempt", 0),
        post_success=analytics.get("post_success", 0),
        post_failed_no_ai=analytics.get("post_failed_no_ai", 0),
        post_failed_groq=analytics.get("post_failed_groq", 0),
        payment_success=analytics.get("payment_success", 0),
        unhandled_error=analytics.get("unhandled_error", 0),
    )


@router.message(Command("admin"))
async def admin_command(message: Message, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    if not _is_admin(message.from_user.id):
        await message.answer(t(language, "admin_denied"))
        return

    runtime = await db.get_runtime_settings()
    suspicious_total = await db.count_suspicious_users()
    recent_flags = await db.get_recent_suspicious_users()
    analytics = await db.get_analytics_summary()
    await message.answer(
        _admin_summary(language, runtime, suspicious_total, recent_flags, analytics),
        reply_markup=admin_panel_keyboard(language),
    )


@router.callback_query(F.data == "admin:refresh")
async def admin_refresh(callback: CallbackQuery, db: Database) -> None:
    language = (await db.get_user_preferences(callback.from_user.id)).language_code
    if not _is_admin(callback.from_user.id):
        await callback.answer(t(language, "admin_denied"), show_alert=True)
        return
    runtime = await db.get_runtime_settings()
    suspicious_total = await db.count_suspicious_users()
    recent_flags = await db.get_recent_suspicious_users()
    analytics = await db.get_analytics_summary()
    await callback.message.edit_text(
        _admin_summary(language, runtime, suspicious_total, recent_flags, analytics),
        reply_markup=admin_panel_keyboard(language),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:set:"))
async def admin_set_prompt(callback: CallbackQuery, state: FSMContext, db: Database) -> None:
    language = (await db.get_user_preferences(callback.from_user.id)).language_code
    if not _is_admin(callback.from_user.id):
        await callback.answer(t(language, "admin_denied"), show_alert=True)
        return

    key = callback.data.split(":", maxsplit=2)[2]
    await state.set_state(AdminState.waiting_for_value)
    await state.update_data(setting_key=key, language=language)
    await callback.answer()
    await callback.message.answer(
        t(
            language,
            "admin_set_prompt",
            setting=_setting_label(language, key),
            hint=t(language, f"admin_hint_{key}"),
        )
    )


@router.message(AdminState.waiting_for_value, F.animation)
async def admin_receive_animation(message: Message, state: FSMContext, db: Database) -> None:
    data = await state.get_data()
    language = data.get("language", "ru")
    if not _is_admin(message.from_user.id):
        await state.clear()
        await message.answer(t(language, "admin_denied"))
        return

    key = data.get("setting_key")
    if key != "brand_animation_id":
        await message.answer(t(language, "admin_unexpected_media"))
        return

    await db.set_runtime_setting("brand_animation_id", message.animation.file_id)
    await state.clear()
    await message.answer(
        t(language, "admin_saved", setting=_setting_label(language, key))
    )


@router.message(AdminState.waiting_for_value, F.sticker)
async def admin_receive_sticker(message: Message, state: FSMContext, db: Database) -> None:
    data = await state.get_data()
    language = data.get("language", "ru")
    if not _is_admin(message.from_user.id):
        await state.clear()
        await message.answer(t(language, "admin_denied"))
        return

    key = data.get("setting_key")
    if key != "brand_sticker_id":
        await message.answer(t(language, "admin_unexpected_media"))
        return

    await db.set_runtime_setting("brand_sticker_id", message.sticker.file_id)
    await state.clear()
    await message.answer(
        t(language, "admin_saved", setting=_setting_label(language, key))
    )


@router.message(AdminState.waiting_for_value)
async def admin_receive_value(message: Message, state: FSMContext, db: Database) -> None:
    data = await state.get_data()
    language = data.get("language", "ru")
    if not _is_admin(message.from_user.id):
        await state.clear()
        await message.answer(t(language, "admin_denied"))
        return

    key = data.get("setting_key")
    text = (message.text or "").strip()
    if not key or not text:
        await message.answer(t(language, "admin_invalid_value"))
        return

    if key in {
        "free_posts_limit",
        "free_generation_cooldown_seconds",
        "max_unique_channels_free",
        "stars_price_14_days",
        "stars_price_30_days",
        "stars_price_90_days",
    }:
        try:
            value = int(text)
        except ValueError:
            await message.answer(t(language, "admin_number_required"))
            return
        if value < 0:
            await message.answer(t(language, "admin_number_required"))
            return
        await db.set_runtime_setting(key, str(value))
    else:
        await db.set_runtime_setting(key, text)

    await state.clear()
    await message.answer(
        t(language, "admin_saved", setting=_setting_label(language, key))
    )
