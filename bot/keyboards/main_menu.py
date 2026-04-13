from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard(language: str, is_admin: bool = False) -> ReplyKeyboardMarkup:
    if language == "en":
        rows = [
            [KeyboardButton(text="/connect"), KeyboardButton(text="/post")],
            [KeyboardButton(text="/ai"), KeyboardButton(text="/ai_status")],
            [KeyboardButton(text="/profile"), KeyboardButton(text="/teach")],
            [KeyboardButton(text="/status"), KeyboardButton(text="/buy")],
            [KeyboardButton(text="/help"), KeyboardButton(text="/setup")],
            [KeyboardButton(text="/faq"), KeyboardButton(text="/reset_all")],
            [KeyboardButton(text="/about"), KeyboardButton(text="/contacts")],
            [KeyboardButton(text="/language en")],
        ]
    else:
        rows = [
            [KeyboardButton(text="/connect"), KeyboardButton(text="/post")],
            [KeyboardButton(text="/ai"), KeyboardButton(text="/ai_status")],
            [KeyboardButton(text="/profile"), KeyboardButton(text="/teach")],
            [KeyboardButton(text="/status"), KeyboardButton(text="/buy")],
            [KeyboardButton(text="/help"), KeyboardButton(text="/setup")],
            [KeyboardButton(text="/faq"), KeyboardButton(text="/reset_all")],
            [KeyboardButton(text="/about"), KeyboardButton(text="/contacts")],
            [KeyboardButton(text="/language ru")],
        ]

    if is_admin:
        rows.append([KeyboardButton(text="/admin")])

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="/help",
    )
