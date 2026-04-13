from __future__ import annotations

import json
import html
import logging
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.config import settings
from bot.database.db import Database, PendingPost
from bot.i18n import t
from bot.keyboards.payments import payment_keyboard
from bot.keyboards.publish import publish_keyboard
from bot.services.channel_parser import get_recent_channel_posts
from bot.services.crypto_prices import CryptoPriceService
from bot.services.fact_research import FactResearchService
from bot.services.groq_ai import GroqAIService
from bot.services.photo_search import PhotoCandidate, PhotoSearchService
from bot.services.secret_box import SecretBox
from bot.services.sticker_selector import StickerSelector


router = Router()
logger = logging.getLogger(__name__)


class PhotoUploadState(StatesGroup):
    waiting_for_custom_photo = State()


class EditPostState(StatesGroup):
    waiting_for_manual_text = State()


def _requires_verified_facts(idea: str) -> bool:
    normalized = idea.casefold().replace("ё", "е")
    fact_markers = (
        "актуальн",
        "конкрет",
        "точн",
        "сколько",
        "убыт",
        "потрат",
        "расход",
        "стоимост",
        "цифр",
        "числ",
        "statistics",
        "stats",
        "exact",
        "specific",
        "how much",
        "losses",
        "spent",
        "cost",
        "numbers",
        "figures",
    )
    date_markers = ("2026", "2025", "апрел", "марта", "today", "yesterday")
    return any(marker in normalized for marker in fact_markers) or any(
        marker in normalized for marker in date_markers
    )


@router.message(Command("post"))
async def generate_post(
    message: Message,
    state: FSMContext,
    db: Database,
    groq_service: GroqAIService,
    photo_service: PhotoSearchService,
    crypto_price_service: CryptoPriceService,
    fact_research_service: FactResearchService,
    secret_box: SecretBox,
    sticker_selector: StickerSelector,
) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    idea = message.text.removeprefix("/post").strip() if message.text else ""
    if not idea:
        await message.answer(t(language, "post_usage"))
        return

    user_id = message.from_user.id
    await db.track_event("post_attempt", user_id=user_id)
    channel_id = await db.get_user_channel(user_id)
    runtime = await db.get_runtime_settings()
    if channel_id is None:
        await message.answer(t(language, "channel_required"))
        return

    access = await db.get_access_status(user_id)
    if not access.has_active_subscription() and access.free_posts_left(runtime.free_posts_limit) <= 0:
        await message.answer(
            t(
                language,
                "free_limit_reached",
                price14=runtime.stars_price_14_days,
                price30=runtime.stars_price_30_days,
                price90=runtime.stars_price_90_days,
            ),
            reply_markup=payment_keyboard(
                language,
                runtime.stars_price_14_days,
                runtime.stars_price_30_days,
                runtime.stars_price_90_days,
            ),
        )
        return

    if (
        not access.has_active_subscription()
        and access.last_free_generation_at
    ):
        last_used_at = datetime.fromisoformat(access.last_free_generation_at)
        now = datetime.now(timezone.utc)
        elapsed = (now - last_used_at).total_seconds()
        if elapsed < runtime.free_generation_cooldown_seconds:
            seconds_left = int(runtime.free_generation_cooldown_seconds - elapsed)
            await db.mark_user_suspicious(
                user_id,
                f"Triggered free generation cooldown ({seconds_left}s left)",
            )
            await db.track_event("post_rejected_cooldown", user_id=user_id)
            await message.answer(
                t(language, "free_cooldown_wait", seconds=seconds_left)
            )
            return

    await state.clear()
    await message.answer(t(language, "post_generating"))

    style_posts = await get_recent_channel_posts(db=db, channel_id=channel_id)
    profile = await db.get_channel_profile(user_id)
    ai_settings = await db.get_user_ai_settings(user_id)
    model_name = settings.groq_model
    api_key_override: str | None = None

    if ai_settings and ai_settings.is_active:
        try:
            api_key_override = secret_box.decrypt(ai_settings.encrypted_api_key)
            model_name = ai_settings.model_name or settings.groq_model
        except Exception as exc:
            logger.warning("Failed to decrypt user AI settings: %s", exc)
            await db.track_event("post_failed_ai_key", user_id=user_id, meta=str(exc))
            await message.answer(t(language, "ai_key_broken"))
            return

    if not api_key_override:
        await db.track_event("post_failed_no_ai", user_id=user_id)
        await message.answer(t(language, "ai_required"))
        return

    facts_context = None
    has_live_data = False
    exact_prices_block = None
    market_image_query = None
    source_payload: list[dict[str, object]] = []

    if crypto_price_service.requires_live_prices(idea):
        await message.answer(t(language, "post_fetching_market_data"))
        try:
            market_snapshot = await crypto_price_service.build_snapshot(idea, language)
            facts_context = market_snapshot.context
            exact_prices_block = market_snapshot.publication_block
            market_image_query = market_snapshot.image_query
            has_live_data = True
            source_payload = market_snapshot.sources
        except Exception as exc:
            logger.warning("Live crypto data fetch failed: %s", exc)
            await db.track_event("post_failed_live_data", user_id=user_id, meta=str(exc))
            await message.answer(
                t(language, "post_live_data_error", error=html.escape(str(exc)))
            )
            return
    elif _requires_verified_facts(idea):
        await message.answer(t(language, "post_fetching_web_facts"))
        try:
            fact_snapshot = await fact_research_service.build_snapshot(idea, language)
            facts_context = fact_snapshot.context
            exact_prices_block = fact_snapshot.publication_block
            market_image_query = fact_snapshot.image_query
            has_live_data = True
            source_payload = [
                {
                    "title": source.title,
                    "url": source.url,
                    "facts": source.facts,
                }
                for source in (fact_snapshot.sources or [])
            ]
        except Exception as exc:
            await db.track_event("post_rejected_fact_request", user_id=user_id, meta=str(exc))
            await message.answer(t(language, "post_fact_mode_required"))
            return

    try:
        generated_draft = await groq_service.generate_post_bundle(
            posts=style_posts,
            idea=idea,
            profile=profile,
            language_code=language,
            facts_context=facts_context,
            api_key_override=api_key_override,
            model_override=model_name,
        )
    except Exception as exc:
        await db.track_event("post_failed_groq", user_id=user_id, meta=str(exc))
        await message.answer(t(language, "post_error", error=html.escape(str(exc))))
        return

    if exact_prices_block and exact_prices_block not in generated_draft.text:
        generated_draft.text = (
            f"{generated_draft.text.rstrip()}\n\n{exact_prices_block}".strip()
        )

    photo = None
    image_query = generated_draft.image_search_query or market_image_query
    if image_query:
        try:
            photo = await photo_service.search_photo(image_query)
        except Exception as exc:
            logger.warning("Photo search failed: %s", exc)

    if photo is not None and len(generated_draft.text) > 1024:
        generated_draft.text = _fit_text_for_media_caption(generated_draft.text)

    sticker_file_id = sticker_selector.pick(generated_draft.sticker_hint)

    pending_post = await db.create_pending_post(
        user_id=user_id,
        channel_id=channel_id,
        idea=idea,
        text=generated_draft.text,
        image_url=photo.url if photo else None,
        image_source_url=photo.source_url if photo else None,
        image_author=photo.author if photo else None,
        image_query=image_query,
        sticker_file_id=sticker_file_id,
        image_provider=photo.provider if photo else None,
        sources_json=json.dumps(source_payload, ensure_ascii=False) if source_payload else None,
    )

    if not access.has_active_subscription():
        await db.increment_free_posts_used(user_id)
    await db.track_event("post_success", user_id=user_id)

    await _send_post_preview(
        message=message,
        pending_post=pending_post,
        has_profile=profile is not None,
        photo=photo,
        language=language,
        has_live_data=has_live_data,
    )


@router.callback_query(F.data.startswith("photo_upload:"))
async def request_custom_photo(
    callback: CallbackQuery,
    state: FSMContext,
    db: Database,
) -> None:
    language = (await db.get_user_preferences(callback.from_user.id)).language_code
    pending_post_id = int(callback.data.split(":", maxsplit=1)[1])
    pending_post = await db.get_pending_post(pending_post_id)
    if pending_post is None:
        await callback.answer(t(language, "draft_not_found"), show_alert=True)
        return
    if callback.from_user.id != pending_post.user_id:
        await callback.answer(t(language, "draft_not_yours"), show_alert=True)
        return

    await state.set_state(PhotoUploadState.waiting_for_custom_photo)
    await state.update_data(pending_post_id=pending_post_id, language=language)
    await callback.answer()
    await callback.message.answer(t(language, "custom_photo_prompt"))


@router.callback_query(F.data.startswith("edit_text:"))
async def request_edit_text(
    callback: CallbackQuery,
    state: FSMContext,
    db: Database,
) -> None:
    language = (await db.get_user_preferences(callback.from_user.id)).language_code
    pending_post_id = int(callback.data.split(":", maxsplit=1)[1])
    pending_post = await db.get_pending_post(pending_post_id)
    if pending_post is None:
        await callback.answer(t(language, "draft_not_found"), show_alert=True)
        return
    if callback.from_user.id != pending_post.user_id:
        await callback.answer(t(language, "draft_not_yours"), show_alert=True)
        return

    await state.set_state(EditPostState.waiting_for_manual_text)
    await state.update_data(pending_post_id=pending_post_id, language=language)
    await callback.answer()
    await callback.message.answer(t(language, "edit_text_prompt"))


@router.message(PhotoUploadState.waiting_for_custom_photo, F.photo)
async def receive_custom_photo(
    message: Message,
    state: FSMContext,
    db: Database,
) -> None:
    data = await state.get_data()
    language = data.get("language", "ru")
    pending_post_id = int(data["pending_post_id"])
    pending_post = await db.get_pending_post(pending_post_id)
    if pending_post is None:
        await state.clear()
        await message.answer(t(language, "draft_not_found"))
        return

    file_id = message.photo[-1].file_id
    await db.set_pending_post_custom_photo(pending_post_id, file_id)
    if len(pending_post.text) > 1024:
        await db.update_pending_post_text(
            pending_post_id,
            _fit_text_for_media_caption(pending_post.text),
        )
    updated_post = await db.get_pending_post(pending_post_id)
    await state.clear()

    await message.answer_photo(
        photo=file_id,
        caption=(
            f"{t(language, 'custom_photo_saved')}\n\n{t(language, 'caption_trimmed_notice')}"
            if len(pending_post.text) > 1024
            else t(language, "custom_photo_saved")
        ),
    )
    await message.answer(
        _build_preview_text(
            language=language,
            post_text=updated_post.text,
            photo_label=t(language, "photo_label_custom"),
            has_sticker=updated_post.sticker_file_id is not None,
            has_profile=await _has_profile(db, updated_post.user_id),
            has_live_data=updated_post.has_sources(),
        ),
        reply_markup=publish_keyboard(
            updated_post.id,
            language,
            has_sources=updated_post.has_sources(),
        ),
    )


@router.message(PhotoUploadState.waiting_for_custom_photo)
async def receive_custom_photo_invalid(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await message.answer(t(data.get("language"), "custom_photo_invalid"))


@router.message(EditPostState.waiting_for_manual_text, F.text)
async def receive_manual_text_edit(
    message: Message,
    state: FSMContext,
    db: Database,
) -> None:
    data = await state.get_data()
    language = data.get("language", "ru")
    pending_post_id = int(data["pending_post_id"])
    pending_post = await db.get_pending_post(pending_post_id)
    if pending_post is None:
        await state.clear()
        await message.answer(t(language, "draft_not_found"))
        return

    new_text = (message.text or "").strip()
    was_trimmed = False
    if (pending_post.custom_photo_file_id or pending_post.image_url) and len(new_text) > 1024:
        new_text = _fit_text_for_media_caption(new_text)
        was_trimmed = True

    await db.update_pending_post_text(pending_post_id, new_text)
    updated_post = await db.get_pending_post(pending_post_id)
    await state.clear()

    response_text = (
        f"{t(language, 'edit_text_saved')}\n\n{t(language, 'caption_trimmed_notice')}"
        if was_trimmed
        else t(language, "edit_text_saved")
    )
    await message.answer(response_text)
    await message.answer(
        _build_preview_text(
            language=language,
            post_text=updated_post.text,
            photo_label=_photo_label_from_pending(updated_post, language),
            has_sticker=updated_post.sticker_file_id is not None,
            has_profile=await _has_profile(db, updated_post.user_id),
            has_live_data=updated_post.has_sources(),
        ),
        reply_markup=publish_keyboard(
            updated_post.id,
            language,
            has_sources=updated_post.has_sources(),
        ),
    )


@router.message(EditPostState.waiting_for_manual_text)
async def receive_manual_text_edit_invalid(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await message.answer(t(data.get("language"), "edit_text_invalid"))


@router.callback_query(F.data.startswith("photo_refresh:"))
async def refresh_photo(
    callback: CallbackQuery,
    db: Database,
    photo_service: PhotoSearchService,
) -> None:
    language = (await db.get_user_preferences(callback.from_user.id)).language_code
    pending_post_id = int(callback.data.split(":", maxsplit=1)[1])
    pending_post = await db.get_pending_post(pending_post_id)

    if pending_post is None:
        await callback.answer(t(language, "draft_not_found"), show_alert=True)
        return
    if callback.from_user.id != pending_post.user_id:
        await callback.answer(t(language, "draft_not_yours"), show_alert=True)
        return
    if not pending_post.image_query:
        await callback.answer(t(language, "photo_refresh_failed"), show_alert=True)
        return

    try:
        photo = await photo_service.search_photo(
            query=pending_post.image_query,
            exclude_url=pending_post.image_url,
        )
    except Exception as exc:
        logger.warning("Photo refresh failed: %s", exc)
        await callback.answer(t(language, "photo_refresh_failed"), show_alert=True)
        return

    if photo is None:
        await callback.answer(t(language, "photo_refresh_none"), show_alert=True)
        return

    await db.update_pending_post_photo(
        pending_post_id=pending_post.id,
        image_url=photo.url,
        image_source_url=photo.source_url,
        image_author=photo.author,
        image_provider=photo.provider,
        custom_photo_file_id=None,
    )
    updated_post = await db.get_pending_post(pending_post.id)
    if len(updated_post.text) > 1024:
        await db.update_pending_post_text(
            updated_post.id,
            _fit_text_for_media_caption(updated_post.text),
        )
        updated_post = await db.get_pending_post(updated_post.id)
    await callback.answer(t(language, "photo_refresh_ok"))
    await _send_photo_preview(callback.message, photo, language)
    await callback.message.answer(
        _build_preview_text(
            language=language,
            post_text=updated_post.text,
            photo_label=_photo_label_from_pending(updated_post, language),
            has_sticker=updated_post.sticker_file_id is not None,
            has_profile=await _has_profile(db, updated_post.user_id),
            has_live_data=updated_post.has_sources(),
        ),
        reply_markup=publish_keyboard(
            updated_post.id,
            language,
            has_sources=updated_post.has_sources(),
        ),
    )


@router.callback_query(F.data.startswith("regenerate:"))
async def regenerate_post(
    callback: CallbackQuery,
    db: Database,
    groq_service: GroqAIService,
    photo_service: PhotoSearchService,
    crypto_price_service: CryptoPriceService,
    fact_research_service: FactResearchService,
    secret_box: SecretBox,
    sticker_selector: StickerSelector,
) -> None:
    language = (await db.get_user_preferences(callback.from_user.id)).language_code
    pending_post_id = int(callback.data.split(":", maxsplit=1)[1])
    pending_post = await db.get_pending_post(pending_post_id)
    if pending_post is None:
        await callback.answer(t(language, "draft_not_found"), show_alert=True)
        return
    if callback.from_user.id != pending_post.user_id:
        await callback.answer(t(language, "draft_not_yours"), show_alert=True)
        return

    await callback.answer()
    await callback.message.answer(t(language, "regenerate_started"))

    ai_settings = await db.get_user_ai_settings(callback.from_user.id)
    if not ai_settings or not ai_settings.is_active:
        await callback.message.answer(t(language, "ai_required"))
        return

    try:
        api_key_override = secret_box.decrypt(ai_settings.encrypted_api_key)
        model_name = ai_settings.model_name or settings.groq_model
    except Exception as exc:
        logger.warning("Failed to decrypt user AI settings during regeneration: %s", exc)
        await callback.message.answer(t(language, "ai_key_broken"))
        return

    style_posts = await get_recent_channel_posts(db=db, channel_id=pending_post.channel_id)
    profile = await db.get_channel_profile(callback.from_user.id)
    facts_context = None
    exact_prices_block = None
    market_image_query = None
    source_payload: list[dict[str, object]] = []
    has_live_data = False

    if crypto_price_service.requires_live_prices(pending_post.idea):
        try:
            market_snapshot = await crypto_price_service.build_snapshot(pending_post.idea, language)
            facts_context = market_snapshot.context
            exact_prices_block = market_snapshot.publication_block
            market_image_query = market_snapshot.image_query
            source_payload = market_snapshot.sources
            has_live_data = True
        except Exception as exc:
            logger.warning("Live crypto data fetch failed during regeneration: %s", exc)
    elif _requires_verified_facts(pending_post.idea):
        try:
            fact_snapshot = await fact_research_service.build_snapshot(pending_post.idea, language)
            facts_context = fact_snapshot.context
            exact_prices_block = fact_snapshot.publication_block
            market_image_query = fact_snapshot.image_query
            source_payload = [
                {"title": source.title, "url": source.url, "facts": source.facts}
                for source in (fact_snapshot.sources or [])
            ]
            has_live_data = True
        except Exception as exc:
            logger.warning("Web fact fetch failed during regeneration: %s", exc)

    try:
        generated_draft = await groq_service.generate_post_bundle(
            posts=style_posts,
            idea=pending_post.idea,
            profile=profile,
            language_code=language,
            facts_context=facts_context,
            api_key_override=api_key_override,
            model_override=model_name,
            variation_instruction=(
                "Сделай новый вариант на ту же тему: другой хук, другой угол, другая структура, "
                "но тот же авторский голос и тот же общий смысл."
            ),
            previous_draft=pending_post.text,
        )
    except Exception as exc:
        await callback.message.answer(t(language, "post_error", error=html.escape(str(exc))))
        return

    if exact_prices_block and exact_prices_block not in generated_draft.text:
        generated_draft.text = f"{generated_draft.text.rstrip()}\n\n{exact_prices_block}".strip()

    image_query = generated_draft.image_search_query or pending_post.image_query or market_image_query
    photo = None
    if image_query:
        try:
            photo = await photo_service.search_photo(
                query=image_query,
                exclude_url=pending_post.image_url,
            )
        except Exception as exc:
            logger.warning("Photo search failed during regeneration: %s", exc)

    new_text = generated_draft.text
    media_exists = bool(pending_post.custom_photo_file_id or photo or pending_post.image_url)
    trimmed_notice = False
    if media_exists and len(new_text) > 1024:
        new_text = _fit_text_for_media_caption(new_text)
        trimmed_notice = True

    await db.update_pending_post_text(pending_post.id, new_text)
    if photo is not None:
        await db.update_pending_post_photo(
            pending_post_id=pending_post.id,
            image_url=photo.url,
            image_source_url=photo.source_url,
            image_author=photo.author,
            image_provider=photo.provider,
            custom_photo_file_id=None,
        )
    updated_post = await db.get_pending_post(pending_post.id)
    updated_post.sources_json = json.dumps(source_payload, ensure_ascii=False) if source_payload else updated_post.sources_json
    updated_post.sticker_file_id = sticker_selector.pick(generated_draft.sticker_hint)

    # Persist extra fields not covered by dedicated DB methods using direct updates.
    await db.update_pending_post_meta(
        pending_post_id=updated_post.id,
        image_query=image_query,
        sticker_file_id=updated_post.sticker_file_id,
        sources_json=updated_post.sources_json,
    )
    updated_post = await db.get_pending_post(updated_post.id)

    if photo is not None:
        await _send_photo_preview(callback.message, photo, language)
    await callback.message.answer(
        f"{t(language, 'regenerate_done')}\n\n{t(language, 'caption_trimmed_notice')}"
        if trimmed_notice
        else t(language, 'regenerate_done')
    )
    await callback.message.answer(
        _build_preview_text(
            language=language,
            post_text=updated_post.text,
            photo_label=_photo_label_from_pending(updated_post, language),
            has_sticker=updated_post.sticker_file_id is not None,
            has_profile=profile is not None,
            has_live_data=has_live_data or updated_post.has_sources(),
        ),
        reply_markup=publish_keyboard(
            updated_post.id,
            language,
            has_sources=updated_post.has_sources(),
        ),
    )


@router.callback_query(F.data.startswith("publish:"))
async def publish_post(callback: CallbackQuery, db: Database) -> None:
    language = (await db.get_user_preferences(callback.from_user.id)).language_code
    pending_post_id = int(callback.data.split(":", maxsplit=1)[1])
    pending_post = await db.get_pending_post(pending_post_id)

    if pending_post is None:
        await callback.answer(t(language, "draft_not_found"), show_alert=True)
        return

    if callback.from_user.id != pending_post.user_id:
        await callback.answer(t(language, "draft_not_yours"), show_alert=True)
        return

    if pending_post.sticker_file_id:
        try:
            await callback.bot.send_sticker(
                chat_id=pending_post.channel_id,
                sticker=pending_post.sticker_file_id,
            )
        except TelegramBadRequest as exc:
            logger.warning("Sticker publish failed: %s", exc)

    published_with_photo = False
    media = pending_post.custom_photo_file_id or pending_post.image_url
    if media:
        try:
            caption_text = _fit_text_for_media_caption(pending_post.text)
            await callback.bot.send_photo(
                chat_id=pending_post.channel_id,
                photo=media,
                caption=html.escape(caption_text),
            )
            published_with_photo = True
        except TelegramBadRequest as exc:
            logger.warning("Photo publish failed: %s", exc)

    if not published_with_photo:
        await callback.bot.send_message(
            chat_id=pending_post.channel_id,
            text=html.escape(pending_post.text),
        )

    await db.delete_pending_post(pending_post.id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer(t(language, "publish_ok"))
    await callback.message.answer(t(language, "publish_success_message"))


@router.callback_query(F.data.startswith("sources:"))
async def show_sources(callback: CallbackQuery, db: Database) -> None:
    language = (await db.get_user_preferences(callback.from_user.id)).language_code
    pending_post_id = int(callback.data.split(":", maxsplit=1)[1])
    pending_post = await db.get_pending_post(pending_post_id)

    if pending_post is None:
        await callback.answer(t(language, "draft_not_found"), show_alert=True)
        return
    if callback.from_user.id != pending_post.user_id:
        await callback.answer(t(language, "draft_not_yours"), show_alert=True)
        return
    if not pending_post.has_sources():
        await callback.answer(t(language, "sources_empty"), show_alert=True)
        return

    await callback.answer()
    await callback.message.answer(_format_sources_text(language, pending_post.sources_json))


async def _send_post_preview(
    message: Message,
    pending_post: PendingPost,
    has_profile: bool,
    photo: PhotoCandidate | None,
    language: str,
    has_live_data: bool,
) -> None:
    if photo is not None:
        await _send_photo_preview(message, photo, language)

    await message.answer(
        _build_preview_text(
            language=language,
            post_text=pending_post.text,
            photo_label=_photo_label_from_pending(pending_post, language),
            has_sticker=pending_post.sticker_file_id is not None,
            has_profile=has_profile,
            has_live_data=has_live_data,
        ),
        reply_markup=publish_keyboard(
            pending_post.id,
            language,
            has_sources=pending_post.has_sources(),
        ),
    )


async def _send_photo_preview(message: Message, photo: PhotoCandidate, language: str) -> None:
    photo_source = (
        t(
            language,
            "photo_source_with_link",
            url=html.escape(photo.source_url),
            provider=html.escape(photo.provider),
        )
        if photo.source_url
        else t(language, "photo_source_plain", provider=html.escape(photo.provider))
    )
    await message.answer_photo(
        photo=photo.url,
        caption=t(
            language,
            "photo_found_caption",
            query=html.escape(photo.query),
            source=photo_source,
            author=html.escape(photo.author),
        ),
    )


async def _has_profile(db: Database, user_id: int) -> bool:
    return await db.get_channel_profile(user_id) is not None


def _context_label(language: str, has_profile: bool, has_live_data: bool) -> str:
    parts: list[str] = []
    if has_profile:
        parts.append(t(language, "preview_context_full"))
    else:
        parts.append(t(language, "preview_context_empty"))
    if has_live_data:
        parts.append(t(language, "preview_context_live_data"))
    return " + ".join(parts)


def _photo_label_from_pending(pending_post: PendingPost, language: str) -> str:
    if pending_post.custom_photo_file_id:
        return t(language, "photo_label_custom")
    if pending_post.image_provider:
        return t(language, "photo_label_provider", provider=pending_post.image_provider)
    if pending_post.image_url:
        return t(language, "photo_label_provider", provider="internet")
    return t(language, "photo_label_none")


def _build_preview_text(
    language: str,
    post_text: str,
    photo_label: str,
    has_sticker: bool,
    has_profile: bool,
    has_live_data: bool,
) -> str:
    extras = [photo_label]
    if has_sticker:
        extras.append(t(language, "sticker_label"))

    extras_text = ", ".join(extras)
    memory_text = _context_label(language, has_profile, has_live_data)
    return t(
        language,
        "preview_title",
        format=html.escape(extras_text),
        context=html.escape(memory_text),
        post_text=html.escape(post_text),
    )


def _format_sources_text(language: str, sources_json: str | None) -> str:
    if not sources_json:
        return t(language, "sources_empty")

    try:
        payload = json.loads(sources_json)
    except json.JSONDecodeError:
        return t(language, "sources_empty")

    if not payload:
        return t(language, "sources_empty")

    blocks = [t(language, "sources_title")]
    for source in payload[:5]:
        title = html.escape(str(source.get("title") or "Source"))
        url = html.escape(str(source.get("url") or ""))
        facts = source.get("facts") or []
        safe_facts = "\n".join(
            f"• {html.escape(str(fact))}" for fact in facts[:4] if str(fact).strip()
        )
        blocks.append(
            t(
                language,
                "sources_block",
                title=title,
                url=url,
                facts=safe_facts or "• —",
            )
        )
    return "\n\n".join(blocks)


def _fit_text_for_media_caption(text: str, limit: int = 1024) -> str:
    cleaned = text.strip()
    if len(cleaned) <= limit:
        return cleaned

    reserve = 1
    candidate = cleaned[: limit - reserve].rstrip()

    paragraph_break = candidate.rfind("\n\n")
    if paragraph_break >= int(limit * 0.55):
        candidate = candidate[:paragraph_break].rstrip()
    else:
        sentence_break = max(candidate.rfind(". "), candidate.rfind("! "), candidate.rfind("? "))
        if sentence_break >= int(limit * 0.6):
            candidate = candidate[: sentence_break + 1].rstrip()
        else:
            word_break = candidate.rfind(" ")
            if word_break >= int(limit * 0.7):
                candidate = candidate[:word_break].rstrip()

    candidate = candidate.rstrip(" .,;:-")
    return f"{candidate}…"
