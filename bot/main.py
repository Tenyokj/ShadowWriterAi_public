import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommandScopeChat

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


async def run_bot() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

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
    dp = Dispatcher()

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

    dp["db"] = db
    dp["groq_service"] = groq_service
    dp["photo_service"] = photo_service
    dp["crypto_price_service"] = crypto_price_service
    dp["fact_research_service"] = fact_research_service
    dp["secret_box"] = secret_box
    dp["sticker_selector"] = sticker_selector

    dp.include_router(admin_router)
    dp.include_router(errors_router)
    dp.include_router(start_router)
    dp.include_router(channel_feed_router)
    dp.include_router(ai_settings_router)
    dp.include_router(connect_router)
    dp.include_router(profile_router)
    dp.include_router(reset_router)
    dp.include_router(payments_router)
    dp.include_router(post_router)

    try:
        if settings.bot_token == DEFAULT_BOT_TOKEN:
            raise ValueError(
                "Укажи реальный TELEGRAM_BOT_TOKEN через переменную окружения."
            )
        if settings.groq_api_key == DEFAULT_GROQ_API_KEY:
            logging.warning(
                "GROQ_API_KEY не задан. Команда /post будет ждать личный AI-ключ пользователя."
            )
        if settings.pixabay_api_key == DEFAULT_PIXABAY_API_KEY and not settings.pexels_api_key:
            logging.warning(
                "PIXABAY_API_KEY и PEXELS_API_KEY не заданы. Посты будут генерироваться без автоподбора фото."
            )
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
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await groq_service.close()
        await photo_service.close()
        await crypto_price_service.close()
        await fact_research_service.close()
        await db.close()


def main() -> None:
    asyncio.run(run_bot())
