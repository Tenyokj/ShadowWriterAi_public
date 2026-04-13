from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.database.db import Database
from bot.i18n import t
from bot.keyboards.main_menu import main_menu_keyboard


router = Router()


class ResetState(StatesGroup):
    waiting_for_confirmation = State()


@router.message(Command(commands=["reset_all", "reset"]))
async def reset_all_command(message: Message, state: FSMContext, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    await state.clear()
    await state.set_state(ResetState.waiting_for_confirmation)
    await state.update_data(language=language)
    await message.answer(t(language, "reset_all_warning"))


@router.message(ResetState.waiting_for_confirmation)
async def confirm_reset_all(message: Message, state: FSMContext, db: Database) -> None:
    data = await state.get_data()
    language = data.get("language", "ru")
    confirmation = (message.text or "").strip()
    expected = "RESET" if language == "en" else "СБРОС"

    if confirmation != expected:
        await state.clear()
        await message.answer(t(language, "reset_all_cancelled"))
        return

    await db.full_reset_user_workspace(message.from_user.id)
    await state.clear()
    await message.answer(
        t(language, "reset_all_done"),
        reply_markup=main_menu_keyboard(language),
    )
