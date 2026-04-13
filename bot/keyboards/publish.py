from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.i18n import t


def publish_keyboard(
    pending_post_id: int,
    language: str,
    has_sources: bool = False,
) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=t(language, "publish_button"),
                callback_data=f"publish:{pending_post_id}",
            ),
            InlineKeyboardButton(
                text=t(language, "edit_text_button"),
                callback_data=f"edit_text:{pending_post_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=t(language, "regenerate_button"),
                callback_data=f"regenerate:{pending_post_id}",
            ),
            InlineKeyboardButton(
                text=t(language, "refresh_photo_button"),
                callback_data=f"photo_refresh:{pending_post_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=t(language, "upload_photo_button"),
                callback_data=f"photo_upload:{pending_post_id}",
            )
        ],
    ]
    if has_sources:
        rows.append(
            [
                InlineKeyboardButton(
                    text=t(language, "show_sources_button"),
                    callback_data=f"sources:{pending_post_id}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)
