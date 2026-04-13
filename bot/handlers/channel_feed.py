from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.database.db import Database
from bot.i18n import t


router = Router()


class TeachState(StatesGroup):
    waiting_for_forwarded_posts = State()


def _extract_text(message: Message) -> str | None:
    text = (message.text or message.caption or "").strip()
    return text or None


def _extract_channel_id(message: Message) -> int | None:
    if message.forward_from_chat is not None and message.forward_from_chat.type == "channel":
        return int(message.forward_from_chat.id)
    forward_origin = getattr(message, "forward_origin", None)
    chat = getattr(forward_origin, "chat", None)
    if chat is not None and getattr(chat, "type", None) == "channel":
        return int(chat.id)
    return None


@router.message(Command("teach"))
async def teach_command(message: Message, state: FSMContext, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    channel_id = await db.get_user_channel(message.from_user.id)
    if channel_id is None:
        await message.answer(t(language, "channel_required"))
        return

    await state.set_state(TeachState.waiting_for_forwarded_posts)
    await state.update_data(channel_id=channel_id, language=language, samples_added=0)
    await message.answer(t(language, "teach_intro"))


@router.message(TeachState.waiting_for_forwarded_posts)
async def teach_receive_forward(message: Message, state: FSMContext, db: Database) -> None:
    data = await state.get_data()
    language = data.get("language", "ru")
    expected_channel_id = int(data["channel_id"])
    text = _extract_text(message)
    forwarded_channel_id = _extract_channel_id(message)

    if (message.text or "").strip().lower() in {"/done", "done"}:
        await state.clear()
        await message.answer(
            t(language, "teach_done", count=int(data.get("samples_added", 0)))
        )
        return

    if forwarded_channel_id != expected_channel_id or not text:
        await message.answer(t(language, "teach_invalid"))
        return

    await db.add_channel_post_sample(
        channel_id=expected_channel_id,
        message_id=message.message_id,
        text=text,
    )
    await db.track_event("channel_sample_added", user_id=message.from_user.id)
    samples_added = int(data.get("samples_added", 0)) + 1
    await state.update_data(samples_added=samples_added)
    await message.answer(t(language, "teach_saved_one", count=samples_added))


@router.channel_post()
async def collect_channel_post(message: Message, db: Database) -> None:
    text = _extract_text(message)
    if not text:
        return
    await db.add_channel_post_sample(
        channel_id=message.chat.id,
        message_id=message.message_id,
        text=text,
    )
