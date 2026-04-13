from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.i18n import t


def admin_panel_keyboard(language: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "admin_free_limit_button"),
                    callback_data="admin:set:free_posts_limit",
                ),
                InlineKeyboardButton(
                    text=t(language, "admin_cooldown_button"),
                    callback_data="admin:set:free_generation_cooldown_seconds",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "admin_unique_channels_button"),
                    callback_data="admin:set:max_unique_channels_free",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "admin_price_14_button"),
                    callback_data="admin:set:stars_price_14_days",
                ),
                InlineKeyboardButton(
                    text=t(language, "admin_price_30_button"),
                    callback_data="admin:set:stars_price_30_days",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "admin_price_90_button"),
                    callback_data="admin:set:stars_price_90_days",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "admin_animation_button"),
                    callback_data="admin:set:brand_animation_id",
                ),
                InlineKeyboardButton(
                    text=t(language, "admin_sticker_button"),
                    callback_data="admin:set:brand_sticker_id",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "admin_about_ru_button"),
                    callback_data="admin:set:about_text_ru",
                ),
                InlineKeyboardButton(
                    text=t(language, "admin_about_en_button"),
                    callback_data="admin:set:about_text_en",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "admin_refresh_button"),
                    callback_data="admin:refresh",
                )
            ],
        ]
    )
