from __future__ import annotations

from aiogram.types import BotCommand


def command_list(language_code: str, is_admin: bool = False) -> list[BotCommand]:
    if language_code == "en":
        commands = [
            BotCommand(command="start", description="Start the bot"),
            BotCommand(command="help", description="Show all commands"),
            BotCommand(command="setup", description="First-time setup guide"),
            BotCommand(command="faq", description="Common issues and fixes"),
            BotCommand(command="cancel", description="Exit the current mode"),
            BotCommand(command="about", description="About the bot"),
            BotCommand(command="contacts", description="Contact the creator"),
            BotCommand(command="language", description="Switch language"),
            BotCommand(command="ai", description="Connect your AI key"),
            BotCommand(command="ai_status", description="Show AI connection"),
            BotCommand(command="ai_disconnect", description="Disconnect AI key"),
            BotCommand(command="connect", description="Connect a channel"),
            BotCommand(command="teach", description="Backfill channel samples"),
            BotCommand(command="profile", description="Set channel memory"),
            BotCommand(command="profile_show", description="Show channel profile"),
            BotCommand(command="post", description="Generate a post"),
            BotCommand(command="status", description="Usage and subscription"),
            BotCommand(command="buy", description="Buy access with Stars"),
            BotCommand(command="groq_help", description="How to get a Groq key"),
            BotCommand(command="terms", description="Terms"),
            BotCommand(command="privacy", description="Privacy and storage"),
            BotCommand(command="paysupport", description="Payment support"),
            BotCommand(command="reset_all", description="Fully reset your workspace"),
        ]
        if is_admin:
            commands.append(BotCommand(command="admin", description="Admin panel"))
        return commands
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Все команды"),
        BotCommand(command="setup", description="Первичная настройка"),
        BotCommand(command="faq", description="Частые проблемы и решения"),
        BotCommand(command="cancel", description="Выйти из текущего режима"),
        BotCommand(command="about", description="О боте"),
        BotCommand(command="contacts", description="Связаться с автором"),
        BotCommand(command="language", description="Сменить язык"),
        BotCommand(command="ai", description="Подключить AI-ключ"),
        BotCommand(command="ai_status", description="Статус AI-ключа"),
        BotCommand(command="ai_disconnect", description="Отключить AI-ключ"),
        BotCommand(command="connect", description="Подключить канал"),
        BotCommand(command="teach", description="Добавить примеры постов"),
        BotCommand(command="profile", description="Заполнить память о канале"),
        BotCommand(command="profile_show", description="Показать профиль канала"),
        BotCommand(command="post", description="Сгенерировать пост"),
        BotCommand(command="status", description="Лимит и подписка"),
        BotCommand(command="buy", description="Купить доступ за Stars"),
        BotCommand(command="groq_help", description="Как получить Groq API key"),
        BotCommand(command="terms", description="Условия"),
        BotCommand(command="privacy", description="Приватность и хранение"),
        BotCommand(command="paysupport", description="Помощь по оплате"),
        BotCommand(command="reset_all", description="Полностью сбросить всё"),
    ]
    if is_admin:
        commands.append(BotCommand(command="admin", description="Админ-панель"))
    return commands
