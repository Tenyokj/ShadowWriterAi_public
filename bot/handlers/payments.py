from __future__ import annotations

from datetime import datetime
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery

from bot.database.db import Database, RuntimeSettings
from bot.i18n import t
from bot.keyboards.payments import payment_keyboard


router = Router()


def _subscription_plans(runtime: RuntimeSettings) -> dict[str, dict[str, int | str]]:
    return {
        "sub_14": {
            "title_ru": "Доступ на 14 дней",
            "title_en": "14-day access",
            "duration_minutes": 14 * 24 * 60,
            "stars": runtime.stars_price_14_days,
        },
        "sub_30": {
            "title_ru": "Доступ на 30 дней",
            "title_en": "30-day access",
            "duration_minutes": 30 * 24 * 60,
            "stars": runtime.stars_price_30_days,
        },
        "sub_90": {
            "title_ru": "Доступ на 90 дней",
            "title_en": "90-day access",
            "duration_minutes": 90 * 24 * 60,
            "stars": runtime.stars_price_90_days,
        },
    }


@router.message(Command("buy"))
async def buy_command(message: Message, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    runtime = await db.get_runtime_settings()
    await message.answer(
        t(language, "buy_intro", limit=runtime.free_posts_limit),
        reply_markup=payment_keyboard(
            language,
            runtime.stars_price_14_days,
            runtime.stars_price_30_days,
            runtime.stars_price_90_days,
        ),
    )


@router.message(Command("status"))
async def status_command(message: Message, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    access = await db.get_access_status(message.from_user.id)
    runtime = await db.get_runtime_settings()
    if access.has_active_subscription():
        expires_at = datetime.fromisoformat(access.subscription_until).strftime("%Y-%m-%d %H:%M UTC")
        await message.answer(
            t(
                language,
                "status_active",
                expires=expires_at,
                used=access.free_posts_used,
            )
        )
        return

    await message.answer(
        t(
            language,
            "status_inactive",
            left=access.free_posts_left(runtime.free_posts_limit),
            limit=runtime.free_posts_limit,
        )
    )


@router.message(Command("terms"))
async def terms_command(message: Message, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    await message.answer(t(language, "terms"))


@router.message(Command("paysupport"))
async def pay_support_command(message: Message, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    await message.answer(t(language, "pay_support"))

@router.callback_query(F.data.startswith("buy:"))
async def buy_callback(callback: CallbackQuery, db: Database) -> None:
    language = (await db.get_user_preferences(callback.from_user.id)).language_code
    runtime = await db.get_runtime_settings()
    plan_code = callback.data.split(":", maxsplit=1)[1]
    plan = _subscription_plans(runtime).get(plan_code)
    if plan is None:
        await callback.answer(t(language, "unknown_plan"), show_alert=True)
        return

    title = str(plan["title_en"] if language == "en" else plan["title_ru"])
    await callback.message.answer_invoice(
        title=title,
        description=t(
            language,
            "invoice_description",
            duration=_human_duration(plan_code, language),
        ),
        payload=plan_code,
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=title, amount=int(plan["stars"]))],
        start_parameter=plan_code,
    )
    await callback.answer()


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, db: Database) -> None:
    runtime = await db.get_runtime_settings()
    if pre_checkout_query.invoice_payload not in _subscription_plans(runtime):
        await pre_checkout_query.answer(ok=False, error_message=t("en", "plan_unavailable"))
        return
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, db: Database) -> None:
    language = (await db.get_user_preferences(message.from_user.id)).language_code
    runtime = await db.get_runtime_settings()
    payment = message.successful_payment
    plan_code = payment.invoice_payload
    plan = _subscription_plans(runtime).get(plan_code)
    if plan is None:
        await message.answer(t(language, "payment_unrecognized"))
        return

    expires_at = await db.activate_subscription(
        user_id=message.from_user.id,
        duration_minutes=int(plan["duration_minutes"]),
        plan_code=plan_code,
        amount=payment.total_amount,
        currency=payment.currency,
        telegram_payment_charge_id=payment.telegram_payment_charge_id,
    )
    expires_human = datetime.fromisoformat(expires_at).strftime("%Y-%m-%d %H:%M UTC")
    title = str(plan["title_en"] if language == "en" else plan["title_ru"])
    await db.track_event("payment_success", user_id=message.from_user.id, meta=plan_code)

    await message.answer(
        t(language, "payment_success", title=title, expires=expires_human)
    )


def _human_duration(plan_code: str, language: str) -> str:
    if plan_code == "sub_14":
        return "14 days" if language == "en" else "14 дней"
    if plan_code == "sub_30":
        return "30 days" if language == "en" else "30 дней"
    if plan_code == "sub_90":
        return "90 days" if language == "en" else "90 дней"
    return "custom duration" if language == "en" else "кастомный срок"
