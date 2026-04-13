from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
import re

from bot.database.db import Database
from bot.i18n import t


router = Router()


class ConnectChannelState(StatesGroup):
    waiting_for_channel_id = State()


@router.message(Command("connect"))
async def connect_command(message: Message, state: FSMContext, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    # Support both the step-by-step flow and `/connect -1001234567890`.
    command_parts = (message.text or "").split(maxsplit=1)
    if len(command_parts) > 1:
        await _save_channel_id(
            message=message,
            state=state,
            db=db,
            raw_channel_id=command_parts[1],
            language=language,
        )
        return

    await state.set_state(ConnectChannelState.waiting_for_channel_id)
    await message.answer(t(language, "connect_prompt"))


@router.message(ConnectChannelState.waiting_for_channel_id)
async def save_channel_id(
    message: Message,
    state: FSMContext,
    db: Database,
) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    channel_id = _extract_forwarded_channel_id(message)
    if channel_id is not None:
        await _save_channel(
            message=message,
            state=state,
            db=db,
            channel_id=channel_id,
            language=language,
        )
        return

    if message.text and re.fullmatch(r"-?\d+", message.text.strip()):
        await _save_channel_id(
            message=message,
            state=state,
            db=db,
            raw_channel_id=message.text.strip(),
            language=language,
        )
        return

    if message.text or message.caption:
        await message.answer(t(language, "connect_forward_missing_metadata"))
        return

    await message.answer(t(language, "connect_waiting"))


async def _save_channel_id(
    message: Message,
    state: FSMContext,
    db: Database,
    raw_channel_id: str,
    language: str,
) -> None:
    try:
        channel_id = int(raw_channel_id)
    except ValueError:
        await message.answer(t(language, "connect_invalid"))
        return

    await _save_channel(
        message=message,
        state=state,
        db=db,
        channel_id=channel_id,
        language=language,
    )


async def _save_channel(
    message: Message,
    state: FSMContext,
    db: Database,
    channel_id: int,
    language: str,
) -> None:
    seen_before = await db.has_user_connected_channel_before(message.from_user.id, channel_id)
    previous_channel_id = await db.get_user_channel(message.from_user.id)
    runtime = await db.get_runtime_settings()
    access = await db.get_access_status(message.from_user.id)
    unique_channels = await db.count_user_unique_channels(message.from_user.id)

    if (
        not seen_before
        and previous_channel_id != channel_id
        and not access.has_active_subscription()
        and unique_channels >= runtime.max_unique_channels_free
    ):
        await db.mark_user_suspicious(
            message.from_user.id,
            f"Exceeded free-tier unique channel limit with channel {channel_id}",
        )
        await db.track_event("connect_rejected_limit", user_id=message.from_user.id)
        await state.clear()
        await message.answer(
            t(
                language,
                "connect_limit_reached",
                limit=runtime.max_unique_channels_free,
            )
        )
        return

    await db.set_user_channel(message.from_user.id, channel_id)
    await db.record_user_channel_history(message.from_user.id, channel_id)
    await db.track_event("channel_connected", user_id=message.from_user.id, meta=str(channel_id))
    switched_channel = previous_channel_id is not None and previous_channel_id != channel_id
    await _save_channel_metadata(
        message=message,
        db=db,
        channel_id=channel_id,
        reset_profile=switched_channel,
    )
    if switched_channel:
        await db.delete_pending_posts_for_user(message.from_user.id)
    await state.clear()
    if seen_before:
        response_key = "connect_success_reused"
    else:
        response_key = "connect_success_switched" if switched_channel else "connect_success"
    await message.answer(t(language, response_key, channel_id=channel_id))


def _extract_forwarded_channel_id(message: Message) -> int | None:
    # Telegram usually fills `forward_from_chat` for forwarded channel posts.
    if message.forward_from_chat is not None and message.forward_from_chat.type == "channel":
        return int(message.forward_from_chat.id)

    # Keep compatibility with the newer `forward_origin` object as well.
    forward_origin = getattr(message, "forward_origin", None)
    chat = getattr(forward_origin, "chat", None)
    if chat is not None and getattr(chat, "type", None) == "channel":
        return int(chat.id)

    return None


async def _save_channel_metadata(
    message: Message,
    db: Database,
    channel_id: int,
    reset_profile: bool,
) -> None:
    channel_title = None
    channel_description = None

    try:
        chat = await message.bot.get_chat(channel_id)
        channel_title = getattr(chat, "title", None)
        channel_description = getattr(chat, "description", None)
    except Exception:
        # The bot can continue working even without auto-fetched metadata.
        pass

    if reset_profile:
        await db.replace_channel_profile(
            user_id=message.from_user.id,
            channel_id=channel_id,
            channel_title=channel_title,
            channel_description=channel_description,
        )
        return

    await db.upsert_channel_profile(
        user_id=message.from_user.id,
        channel_id=channel_id,
        channel_title=channel_title,
        channel_description=channel_description,
    )
