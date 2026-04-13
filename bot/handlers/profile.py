from __future__ import annotations

import html

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.database.db import ChannelProfile, Database
from bot.i18n import t


router = Router()
SKIP_VALUE = "-"


class ProfileSetupState(StatesGroup):
    waiting_for_topic = State()
    waiting_for_audience = State()
    waiting_for_admin_persona = State()
    waiting_for_content_pillars = State()
    waiting_for_style_notes = State()
    waiting_for_banned_topics = State()


@router.message(Command("profile"))
async def profile_command(message: Message, state: FSMContext, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    channel_id = await db.get_user_channel(message.from_user.id)
    if channel_id is None:
        await message.answer(t(language, "profile_required"))
        return

    profile = await db.get_channel_profile(message.from_user.id)
    await state.clear()
    await state.update_data(channel_id=channel_id, language=language)
    await state.set_state(ProfileSetupState.waiting_for_topic)

    summary = _profile_summary(profile, language)
    await message.answer(t(language, "profile_intro", summary=summary))


@router.message(Command("profile_show"))
async def profile_show_command(message: Message, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    profile = await db.get_channel_profile(message.from_user.id)
    if profile is None:
        await message.answer(t(language, "profile_empty"))
        return
    await message.answer(_profile_summary(profile, language))


@router.message(ProfileSetupState.waiting_for_topic)
async def profile_topic(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.update_data(channel_topic=_clean_value(message.text))
    await state.set_state(ProfileSetupState.waiting_for_audience)
    await message.answer(t(data.get("language"), "profile_q2"))


@router.message(ProfileSetupState.waiting_for_audience)
async def profile_audience(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.update_data(target_audience=_clean_value(message.text))
    await state.set_state(ProfileSetupState.waiting_for_admin_persona)
    await message.answer(t(data.get("language"), "profile_q3"))


@router.message(ProfileSetupState.waiting_for_admin_persona)
async def profile_admin_persona(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.update_data(admin_persona=_clean_value(message.text))
    await state.set_state(ProfileSetupState.waiting_for_content_pillars)
    await message.answer(t(data.get("language"), "profile_q4"))


@router.message(ProfileSetupState.waiting_for_content_pillars)
async def profile_content_pillars(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.update_data(content_pillars=_clean_value(message.text))
    await state.set_state(ProfileSetupState.waiting_for_style_notes)
    await message.answer(t(data.get("language"), "profile_q5"))


@router.message(ProfileSetupState.waiting_for_style_notes)
async def profile_style_notes(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.update_data(style_notes=_clean_value(message.text))
    await state.set_state(ProfileSetupState.waiting_for_banned_topics)
    await message.answer(t(data.get("language"), "profile_q6"))


@router.message(ProfileSetupState.waiting_for_banned_topics)
async def profile_banned_topics(
    message: Message,
    state: FSMContext,
    db: Database,
) -> None:
    data = await state.get_data()
    language = data.get("language")
    await state.update_data(banned_topics=_clean_value(message.text))
    await db.upsert_channel_profile(
        user_id=message.from_user.id,
        channel_id=int(data["channel_id"]),
        channel_topic=data.get("channel_topic"),
        target_audience=data.get("target_audience"),
        admin_persona=data.get("admin_persona"),
        content_pillars=data.get("content_pillars"),
        style_notes=data.get("style_notes"),
        banned_topics=data.get("banned_topics"),
    )
    profile = await db.get_channel_profile(message.from_user.id)
    await state.clear()
    await message.answer(t(language, "profile_saved", summary=_profile_summary(profile, language)))


def _clean_value(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    if not text or text == SKIP_VALUE:
        return None
    return text


def _profile_summary(profile: ChannelProfile | None, language: str) -> str:
    if profile is None:
        return t(language, "profile_empty")

    lines = [
        t(language, "profile_summary_title"),
        f"Title: {html.escape(profile.channel_title or 'not set')}" if language == "en" else f"Название: {html.escape(profile.channel_title or 'не задано')}",
        f"Description: {html.escape(profile.channel_description or 'not set')}" if language == "en" else f"Описание: {html.escape(profile.channel_description or 'не задано')}",
        f"Topic: {html.escape(profile.channel_topic or 'not set')}" if language == "en" else f"Тема: {html.escape(profile.channel_topic or 'не задано')}",
        f"Audience: {html.escape(profile.target_audience or 'not set')}" if language == "en" else f"Аудитория: {html.escape(profile.target_audience or 'не задано')}",
        f"Author persona: {html.escape(profile.admin_persona or 'not set')}" if language == "en" else f"Образ автора: {html.escape(profile.admin_persona or 'не задано')}",
        f"Content pillars: {html.escape(profile.content_pillars or 'not set')}" if language == "en" else f"Рубрики: {html.escape(profile.content_pillars or 'не задано')}",
        f"Style: {html.escape(profile.style_notes or 'not set')}" if language == "en" else f"Стиль: {html.escape(profile.style_notes or 'не задано')}",
        f"Banned topics: {html.escape(profile.banned_topics or 'not set')}" if language == "en" else f"Стоп-темы: {html.escape(profile.banned_topics or 'не задано')}",
    ]
    return "\n".join(lines)
