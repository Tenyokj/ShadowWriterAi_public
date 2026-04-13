from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.i18n import t

def payment_keyboard(
    language: str,
    price_14: int,
    price_30: int,
    price_90: int,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "buy_14_button", price=price_14),
                    callback_data="buy:sub_14",
                ),
                InlineKeyboardButton(
                    text=t(language, "buy_30_button", price=price_30),
                    callback_data="buy:sub_30",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "buy_90_button", price=price_90),
                    callback_data="buy:sub_90",
                ),
            ],
        ]
    )
