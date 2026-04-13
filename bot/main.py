import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommandScopeChat
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from bot.commands import command_list
from bot.config import (
    DEFAULT_BOT_TOKEN,
    DEFAULT_GROQ_API_KEY,
    DEFAULT_PIXABAY_API_KEY,
    settings,
)
from bot.database.db import Database
from bot.handlers.ai_settings import router as ai_settings_router
from bot.handlers.admin import router as admin_router
from bot.handlers.channel_feed import router as channel_feed_router
from bot.handlers.connect import router as connect_router
from bot.handlers.errors import router as errors_router
from bot.handlers.payments import router as payments_router
from bot.handlers.post import router as post_router
from bot.handlers.profile import router as profile_router
from bot.handlers.reset import router as reset_router
from bot.handlers.start import router as start_router
from bot.services.crypto_prices import CryptoPriceService
from bot.services.fact_research import FactResearchService
from bot.services.groq_ai import GroqAIService
from bot.services.photo_search import PhotoSearchService
from bot.services.secret_box import SecretBox
from bot.services.sticker_selector import StickerSelector


@dataclass(slots=True)
class AppRuntime:
    db: Database
    bot: Bot
    dispatcher: Dispatcher
    groq_service: GroqAIService
    photo_service: PhotoSearchService
    crypto_price_service: CryptoPriceService
    fact_research_service: FactResearchService


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def _register_routers(dispatcher: Dispatcher) -> None:
    dispatcher.include_router(admin_router)
    dispatcher.include_router(errors_router)
    dispatcher.include_router(start_router)
    dispatcher.include_router(channel_feed_router)
    dispatcher.include_router(ai_settings_router)
    dispatcher.include_router(connect_router)
    dispatcher.include_router(profile_router)
    dispatcher.include_router(reset_router)
    dispatcher.include_router(payments_router)
    dispatcher.include_router(post_router)


async def _configure_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(command_list("en"))
    await bot.set_my_commands(command_list("ru"), language_code="ru")
    await bot.set_my_commands(command_list("en"), language_code="en")
    if settings.admin_user_id > 0:
        await bot.set_my_commands(
            command_list("ru", is_admin=True),
            scope=BotCommandScopeChat(chat_id=settings.admin_user_id),
            language_code="ru",
        )
        await bot.set_my_commands(
            command_list("en", is_admin=True),
            scope=BotCommandScopeChat(chat_id=settings.admin_user_id),
            language_code="en",
        )


def _validate_settings() -> None:
    if settings.bot_token == DEFAULT_BOT_TOKEN:
        raise ValueError(
            "Set a real TELEGRAM_BOT_TOKEN through environment variables."
        )
    if settings.groq_api_key == DEFAULT_GROQ_API_KEY:
        logging.warning(
            "GROQ_API_KEY is not set. /post will require each user to connect a personal AI key."
        )
    if settings.pixabay_api_key == DEFAULT_PIXABAY_API_KEY and not settings.pexels_api_key:
        logging.warning(
            "PIXABAY_API_KEY and PEXELS_API_KEY are not set. Auto photo lookup will be unavailable."
        )
    if settings.use_webhook and not settings.webhook_url:
        raise ValueError(
            "WEBHOOK_BASE_URL is set incorrectly. Render deployment requires a valid public webhook URL."
        )


async def _build_runtime() -> AppRuntime:
    db = Database()
    await db.connect()
    await db.init()
    logging.info(
        "Database backend: %s",
        "PostgreSQL" if settings.database_url else "SQLite",
    )

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher()

    groq_service = GroqAIService(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        api_url=settings.groq_api_url,
        models_api_url=settings.groq_models_api_url,
    )
    photo_service = PhotoSearchService(
        pixabay_api_key=settings.pixabay_api_key,
        pixabay_api_url=settings.pixabay_api_url,
        pexels_api_key=settings.pexels_api_key,
        pexels_api_url=settings.pexels_api_url,
    )
    crypto_price_service = CryptoPriceService(
        api_url=settings.coingecko_price_api_url,
    )
    fact_research_service = FactResearchService()
    secret_box = SecretBox(settings.master_encryption_key)
    sticker_selector = StickerSelector(
        {
            "fire": settings.sticker_fire_id,
            "idea": settings.sticker_idea_id,
            "news": settings.sticker_news_id,
            "wow": settings.sticker_wow_id,
        }
    )

    dispatcher["db"] = db
    dispatcher["groq_service"] = groq_service
    dispatcher["photo_service"] = photo_service
    dispatcher["crypto_price_service"] = crypto_price_service
    dispatcher["fact_research_service"] = fact_research_service
    dispatcher["secret_box"] = secret_box
    dispatcher["sticker_selector"] = sticker_selector
    _register_routers(dispatcher)

    return AppRuntime(
        db=db,
        bot=bot,
        dispatcher=dispatcher,
        groq_service=groq_service,
        photo_service=photo_service,
        crypto_price_service=crypto_price_service,
        fact_research_service=fact_research_service,
    )


async def _close_runtime(runtime: AppRuntime, close_bot_session: bool) -> None:
    if close_bot_session:
        await runtime.bot.session.close()
    await runtime.groq_service.close()
    await runtime.photo_service.close()
    await runtime.crypto_price_service.close()
    await runtime.fact_research_service.close()
    await runtime.db.close()


async def _run_polling() -> None:
    runtime = await _build_runtime()
    try:
        await _configure_bot_commands(runtime.bot)
        await runtime.dispatcher.start_polling(runtime.bot)
    finally:
        await _close_runtime(runtime, close_bot_session=True)


async def _healthcheck(_: web.Request) -> web.Response:
    return web.Response(text="ok")


async def _webhook_startup(bot: Bot, dispatcher: Dispatcher, **_: Any) -> None:
    await _configure_bot_commands(bot)
    await bot.set_webhook(
        url=settings.webhook_url,
        secret_token=settings.webhook_secret or None,
        allowed_updates=dispatcher.resolve_used_update_types(),
    )
    logging.info("Webhook mode enabled: %s", settings.webhook_url)


async def _webhook_shutdown(
    bot: Bot,
    runtime: AppRuntime,
    **_: Any,
) -> None:
    await bot.delete_webhook(drop_pending_updates=False)
    await _close_runtime(runtime, close_bot_session=False)


async def _create_web_app() -> web.Application:
    runtime = await _build_runtime()
    runtime.dispatcher.startup.register(_webhook_startup)
    runtime.dispatcher.shutdown.register(_webhook_shutdown)

    app = web.Application()
    app["runtime"] = runtime
    app.router.add_get("/", _healthcheck)
    app.router.add_get("/healthz", _healthcheck)

    webhook_handler = SimpleRequestHandler(
        dispatcher=runtime.dispatcher,
        bot=runtime.bot,
        secret_token=settings.webhook_secret or None,
    )
    webhook_handler.register(app, path=settings.normalized_webhook_path)
    setup_application(app, runtime.dispatcher, bot=runtime.bot, runtime=runtime)
    return app


def main() -> None:
    _configure_logging()
    _validate_settings()
    if settings.use_webhook:
        web.run_app(
            _create_web_app(),
            host=settings.web_server_host,
            port=settings.web_server_port,
        )
        return
    asyncio.run(_run_polling())
