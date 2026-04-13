from __future__ import annotations

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommandScopeChat
from aiogram.types import Message

from bot.commands import command_list
from bot.config import settings
from bot.database.db import Database
from bot.i18n import normalize_language, t
from bot.keyboards.main_menu import main_menu_keyboard


router = Router()


def _is_admin(user_id: int) -> bool:
    return settings.admin_user_id > 0 and user_id == settings.admin_user_id


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext, db: Database) -> None:
    language = "en"
    await state.clear()
    await db.set_user_language(message.from_user.id, language)
    await message.bot.set_my_commands(
        command_list(language, is_admin=_is_admin(message.from_user.id)),
        scope=BotCommandScopeChat(chat_id=message.from_user.id),
    )
    await db.track_event("start_command", user_id=message.from_user.id)
    runtime = await db.get_runtime_settings()
    if runtime.brand_animation_id:
        try:
            await message.answer_animation(runtime.brand_animation_id)
        except TelegramBadRequest:
            pass
    if runtime.brand_sticker_id:
        try:
            await message.answer_sticker(runtime.brand_sticker_id)
        except TelegramBadRequest:
            pass
    await message.answer(
        t(language, "start_message"),
        reply_markup=main_menu_keyboard(language, is_admin=_is_admin(message.from_user.id)),
    )


@router.message(Command("help"))
async def help_command(message: Message, state: FSMContext, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    await state.clear()
    await message.answer(
        t(language, "help_message"),
        reply_markup=main_menu_keyboard(language, is_admin=_is_admin(message.from_user.id)),
    )


@router.message(Command("setup"))
async def setup_command(message: Message, state: FSMContext, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    await state.clear()
    await message.answer(
        t(language, "setup_message"),
        reply_markup=main_menu_keyboard(language, is_admin=_is_admin(message.from_user.id)),
    )


@router.message(Command("faq"))
async def faq_command(message: Message, state: FSMContext, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    await state.clear()
    await message.answer(
        t(language, "faq_message"),
        reply_markup=main_menu_keyboard(language, is_admin=_is_admin(message.from_user.id)),
    )


@router.message(Command("about"))
async def about_command(message: Message, state: FSMContext, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    await state.clear()
    runtime = await db.get_runtime_settings()
    about_text = runtime.about_text_en if language == "en" else runtime.about_text_ru
    await message.answer(
        about_text or t(language, "about_message"),
        reply_markup=main_menu_keyboard(language, is_admin=_is_admin(message.from_user.id)),
    )


@router.message(Command("contacts"))
async def contacts_command(message: Message, state: FSMContext, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    await state.clear()
    await message.answer(
        t(language, "contacts_message"),
        reply_markup=main_menu_keyboard(language, is_admin=_is_admin(message.from_user.id)),
    )


@router.message(Command("privacy"))
async def privacy_command(message: Message, state: FSMContext, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    await state.clear()
    await message.answer(
        t(language, "privacy"),
        reply_markup=main_menu_keyboard(language, is_admin=_is_admin(message.from_user.id)),
    )


@router.message(Command("language"))
async def language_command(message: Message, state: FSMContext, db: Database) -> None:
    parts = (message.text or "").split(maxsplit=1)
    await state.clear()
    if len(parts) < 2:
        current_language = (await db.get_user_preferences(message.from_user.id)).language_code
        await message.answer(t(current_language, "language_usage"))
        return

    language_code = normalize_language(parts[1].strip().lower())
    await db.set_user_language(message.from_user.id, language_code)
    await message.bot.set_my_commands(
        command_list(language_code, is_admin=_is_admin(message.from_user.id)),
        scope=BotCommandScopeChat(chat_id=message.from_user.id),
    )
    await message.bot.set_my_commands(command_list("ru"), language_code="ru")
    await message.bot.set_my_commands(command_list("en"), language_code="en")
    if _is_admin(message.from_user.id):
        await message.bot.set_my_commands(
            command_list("ru", is_admin=True),
            scope=BotCommandScopeChat(chat_id=message.from_user.id),
            language_code="ru",
        )
        await message.bot.set_my_commands(
            command_list("en", is_admin=True),
            scope=BotCommandScopeChat(chat_id=message.from_user.id),
            language_code="en",
        )
    await message.answer(
        t(language_code, f"language_set_{language_code}"),
        reply_markup=main_menu_keyboard(language_code, is_admin=_is_admin(message.from_user.id)),
    )


@router.message(Command("cancel"))
async def cancel_command(message: Message, state: FSMContext, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    await state.clear()
    await message.answer(
        t(language, "cancel_done"),
        reply_markup=main_menu_keyboard(language, is_admin=_is_admin(message.from_user.id)),
    )


@router.message(lambda message: message.sticker is not None)
async def sticker_debug(message: Message, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    await message.answer(
        t(
            language,
            "sticker_debug_message",
            file_id=message.sticker.file_id,
            file_unique_id=message.sticker.file_unique_id,
        )
    )


@router.message(lambda message: message.animation is not None)
async def animation_debug(message: Message, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    await message.answer(
        t(
            language,
            "animation_debug_message",
            file_id=message.animation.file_id,
            file_unique_id=message.animation.file_unique_id,
        )
    )


@router.message(lambda message: message.video is not None)
async def video_debug(message: Message, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    await message.answer(
        t(
            language,
            "video_debug_message",
            file_id=message.video.file_id,
            file_unique_id=message.video.file_unique_id,
        )
    )
