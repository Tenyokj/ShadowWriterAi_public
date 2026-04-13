from __future__ import annotations

from typing import Any


DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = {"ru", "en"}


TEXTS: dict[str, dict[str, str]] = {
    "ru": {
        "start_message": (
            "<b>AI Shadow Writer</b>\n"
            "<i>Telegram channel writing system</i>\n\n"
            "<blockquote>⌁ Turns raw ideas into channel-ready drafts that feel authored, not mechanically generated.</blockquote>\n\n"
            "<b>◦ Inside</b>\n"
            "◦ bring your own AI key via <code>/ai</code>\n"
            "◦ channel memory and author voice\n"
            "◦ photo search, replacement, and publishing\n"
            "◦ English / Russian workflow\n"
            "◦ limits and Telegram Stars access\n\n"
            "<b>◦ Quick start</b>\n"
            "1. <code>/ai</code>\n"
            "2. <code>/connect</code>\n"
            "3. <code>/profile</code>\n"
            "4. <code>/post idea</code>\n\n"
            "<i>⌁ The menu below is ready for faster navigation.</i>"
        ),
        "help_message": (
            "<b>Command Center</b>\n\n"
            "<blockquote>⌁ Everything below affects the bot interface only. Generated post drafts keep their own style.</blockquote>\n\n"
            "<b>◦ Setup</b>\n"
            "◦ <code>/ai</code> — connect your personal Groq API key\n"
            "◦ <code>/groq_help</code> — where to get a Groq API key\n"
            "◦ <code>/ai_status</code> — show current AI connection\n"
            "◦ <code>/ai_disconnect</code> — remove your AI key\n"
            "◦ <code>/connect</code> — connect a channel\n"
            "◦ <code>/teach</code> — add real channel post samples\n"
            "◦ <code>/profile</code> — fill channel memory\n"
            "◦ <code>/profile_show</code> — show saved profile\n\n"
            "<b>◦ Content</b>\n"
            "◦ <code>/post &lt;idea&gt;</code> — generate a post draft\n"
            "◦ use the buttons under a draft to edit text, regenerate, or swap the photo\n\n"
            "<b>◦ Access</b>\n"
            "◦ <code>/status</code> — usage and subscription\n"
            "◦ <code>/buy</code> — unlock access with Stars\n"
            "◦ paid access is handled through Telegram Stars\n\n"
            "<b>◦ Info</b>\n"
            "◦ <code>/about</code> — about the bot\n"
            "◦ <code>/contacts</code> — creator contacts and links\n"
            "◦ <code>/language ru|en</code> — interface + post language\n"
            "◦ <code>/terms</code> — terms\n"
            "◦ <code>/privacy</code> — privacy and storage\n"
            "◦ <code>/paysupport</code> — payment support"
        ),
        "setup_message": (
            "<b>Setup Guide</b>\n\n"
            "<blockquote>⌁ Before the bot can publish to your channel, it must be added to that channel as an admin with posting rights.</blockquote>\n\n"
            "<b>◦ Step by step</b>\n"
            "1. Add the bot to your Telegram channel as an admin\n"
            "2. Make sure it has permission to publish posts\n"
            "3. Open <code>/groq_help</code> and create your Groq API key\n"
            "4. Send <code>/ai</code> and connect that key\n"
            "5. Send <code>/connect</code> and forward any post from the channel, or send the channel ID manually\n"
            "6. Fill in <code>/profile</code> so the bot understands the channel voice\n"
            "7. Optionally use <code>/teach</code> and forward 3-10 older posts from the same channel\n"
            "8. Generate a draft with <code>/post your idea</code>\n"
            "9. Review the draft, adjust text or photo, then publish\n\n"
            "<b>◦ Important</b>\n"
            "◦ no admin rights = no publishing\n"
            "◦ no Groq key = no generation\n"
            "◦ no connected channel = nowhere to publish"
        ),
        "faq_message": (
            "<b>FAQ</b>\n\n"
            "<blockquote>⌁ If something looks broken, most often it is one of the setup conditions below.</blockquote>\n\n"
            "<b>◦ Why can't the bot publish to my channel?</b>\n"
            "◦ the bot was not added as an admin\n"
            "◦ or it does not have permission to publish posts\n\n"
            "<b>◦ Why does /post not work?</b>\n"
            "◦ your personal Groq API key is not connected yet\n"
            "◦ use <code>/groq_help</code> then <code>/ai</code>\n\n"
            "<b>◦ Why does /connect fail?</b>\n"
            "◦ the forwarded post may hide channel metadata\n"
            "◦ try forwarding another post or send the channel ID manually\n\n"
            "<b>◦ Why is the style weak or generic?</b>\n"
            "◦ fill in <code>/profile</code>\n"
            "◦ then use <code>/teach</code> with real older channel posts\n\n"
            "<b>◦ Why is the photo wrong?</b>\n"
            "◦ use the buttons under the draft to swap the photo or upload your own\n\n"
            "<b>◦ Why does the bot answer in the wrong language?</b>\n"
            "◦ switch it with <code>/language en</code> or <code>/language ru</code>"
        ),
        "about_message": (
            "<b>About AI Shadow Writer</b>\n\n"
            "<blockquote>⌁ MVP-система для админов Telegram-каналов, которым нужен аккуратный AI-редактор с памятью о канале, визуалом и быстрым выпуском постов.</blockquote>\n\n"
            "<b>◦ Как это работает</b>\n"
            "◦ продукт оплачивается внутри бота\n"
            "◦ генерация идёт через личный AI-ключ пользователя\n"
            "◦ бот хранит контекст канала и ускоряет выпуск контента\n\n"
            "<b>◦ Сильные стороны</b>\n"
            "◦ пишет в контексте канала, а не абстрактного интернета\n"
            "◦ умеет работать с визуалом\n"
            "◦ поддерживает RU / EN\n"
            "◦ открывает доступ через Telegram Stars\n\n"
            "<b>◦ Автор</b>\n"
            "Tenyokj · Shadow Writer AI"
        ),
        "contacts_message": (
            "<b>Contacts</b>\n\n"
            "<blockquote>⌁ Reach out for launch questions, bugs, ideas, or collaboration.</blockquote>\n\n"
            "◦ Email: <a href=\"mailto:dv842449@gmail.com\">dv842449@gmail.com</a>\n"
            "◦ Telegram: <a href=\"https://t.me/tenkoffj\">@tenkoffj</a>\n"
            "◦ GitHub: <a href=\"https://github.com/Tenyokj\">Tenyokj</a>\n"
            "◦ Website: <a href=\"https://tenyokj.vercel.app/\">tenyokj.vercel.app</a>\n\n"
            "<i>⌁ Telegram is the fastest way to reach me.</i>"
        ),
        "language_set_ru": "Язык переключён на русский. Теперь и интерфейс, и посты будут на русском.",
        "language_set_en": "Language switched to English. Now both the interface and generated posts will be in English.",
        "language_usage": "Используй <code>/language ru</code> или <code>/language en</code>.",
        "cancel_done": "⌁ Текущий режим сброшен. Идём дальше с чистого состояния.",
        "ai_intro": (
            "<b>Подключение AI</b>\n\n"
            "1. Создай API key в Groq\n"
            "2. Отправь его следующим сообщением сюда\n"
            "3. Я зашифрую ключ и буду использовать его только для твоих генераций\n\n"
            "Текущая модель по умолчанию: <code>{model}</code>"
        ),
        "groq_help_message": (
            "<b>Groq API Key Guide</b>\n\n"
            "<blockquote>⌁ Это нужно сделать один раз. После этого бот будет использовать твой собственный Groq API key.</blockquote>\n\n"
            "<b>◦ Шаги</b>\n"
            "1. Открой <a href=\"https://console.groq.com/keys\">console.groq.com/keys</a>\n"
            "2. Войди в аккаунт или создай его\n"
            "3. Создай новый API key\n"
            "4. Скопируй ключ\n"
            "5. Вернись сюда и отправь <code>/ai</code>\n"
            "6. В следующем сообщении вставь ключ\n\n"
            "<b>◦ Важно</b>\n"
            "◦ ключ хранится в зашифрованном виде\n"
            "◦ бот использует твои собственные лимиты Groq\n"
            "◦ когда ты пришлёшь своё обучающее видео, я смогу прикрепить его к этой команде"
        ),
        "ai_validating": "Проверяю ключ Groq...",
        "ai_connected": "AI-ключ подключён ✅\nТеперь /post будет работать через твой Groq key.\nМодель: <code>{model}</code>",
        "ai_status_empty": "Личный AI-ключ пока не подключён.\nИспользуй <code>/ai</code>.\nМодель по умолчанию: <code>{model}</code>",
        "ai_status_connected": "AI подключён ✅\nПровайдер: <code>{provider}</code>\nМодель: <code>{model}</code>",
        "ai_disconnected": "Личный AI-ключ удалён. Если глобальный ключ сервера не настроен, /post попросит снова пройти <code>/ai</code>.",
        "ai_required": "Сначала подключи свой AI-ключ через <code>/ai</code>. Без него я не смогу генерировать посты.",
        "ai_storage_not_ready": "На сервере пока не настроено безопасное хранилище для ключей. Нужно задать <code>MASTER_ENCRYPTION_KEY</code>.",
        "ai_key_invalid": "Пришли именно API key одним сообщением, без команды и без лишнего текста.",
        "ai_key_check_failed": "Не удалось проверить этот Groq key.\nТехническая ошибка: <code>{error}</code>",
        "ai_key_broken": "Не удалось расшифровать или прочитать твой сохранённый AI-ключ. Подключи его заново через <code>/ai</code>.",
        "connect_prompt": (
            "<b>Connect Channel</b>\n\n"
            "<blockquote>⌁ Перешли любой пост из канала, и я сам попробую определить его ID.</blockquote>\n\n"
            "◦ можно прислать ID вручную: <code>-1001234567890</code>\n"
            "◦ перед этим добавь бота в канал\n"
            "◦ и выдай ему права на публикацию"
        ),
        "teach_intro": (
            "Теперь можешь обучить бота на реальных старых постах канала.\n"
            "Перешли сюда 3-10 старых постов именно из подключённого канала.\n"
            "Когда закончишь, отправь <code>/done</code>. Если передумал, отправь <code>/cancel</code>."
        ),
        "teach_invalid": "Сейчас включён режим /teach. Нужен пересланный пост именно из текущего подключённого канала с непустым текстом. Для выхода используй <code>/done</code> или <code>/cancel</code>.",
        "teach_saved_one": "Сохранил пример поста. Уже добавлено: <code>{count}</code>.",
        "teach_done": "Готово. Сохранил примеров: <code>{count}</code>. Теперь генерация будет лучше чувствовать реальный стиль канала.",
        "connect_success": (
            "Канал <code>{channel_id}</code> подключён. Теперь можно использовать "
            "<code>/post идея поста</code>.\n"
            "Чтобы бот писал ближе к голосу автора, заполни ещё <code>/profile</code>."
        ),
        "connect_success_switched": (
            "Новый канал <code>{channel_id}</code> подключён.\n"
            "Память прошлого канала я сбросил, чтобы она не протекала в новый.\n"
            "Теперь заново заполни <code>/profile</code> для этого канала.\n\n"
            "Лимиты, подписка и AI-ключ при этом не сбрасываются. Для полного старта с нуля используй <code>/reset_all</code>."
        ),
        "connect_success_reused": (
            "Канал <code>{channel_id}</code> снова подключён.\n"
            "Я сохранил факт, что этот канал уже использовался этим аккаунтом, поэтому бесплатные лимиты и платёжный статус не начинаются заново.\n"
            "Если нужно, просто заново заполни <code>/profile</code> для этого канала."
        ),
        "connect_waiting": "Я жду либо пересланный пост из канала, либо его ID в формате <code>-1001234567890</code>.",
        "connect_forward_missing_metadata": (
            "Telegram не передал мне metadata канала в этом пересланном сообщении.\n"
            "Так бывает, если у канала включена защита контента или форвард пришёл без origin-данных.\n\n"
            "Что сделать:\n"
            "• отправь ID канала вручную в формате <code>-1001234567890</code>\n"
            "• или перешли другой пост из этого канала\n"
            "• и проверь, что бот добавлен в канал как администратор"
        ),
        "connect_invalid": "Похоже, это не похоже на ID канала. Пример: <code>-1001234567890</code>.",
        "channel_required": "Сначала подключи канал через <code>/connect</code>, чтобы я знал, куда публиковать.",
        "post_usage": "Используй формат: <code>/post идея поста</code>.",
        "post_generating": "Генерирую пост в стиле канала, это займёт пару секунд...",
        "post_fetching_market_data": "Подтягиваю актуальные рыночные данные, чтобы пост был с точными цифрами...",
        "post_fetching_web_facts": "Ищу подтверждённые факты и цифры в веб-источниках...",
        "post_error": "Не удалось получить ответ от Groq API. Проверь ключ и настройки модели.\nТехническая ошибка: <code>{error}</code>",
        "post_live_data_error": "Не удалось получить актуальные рыночные данные.\nБез них я не буду выдумывать цифры.\nТехническая ошибка: <code>{error}</code>",
        "post_fact_mode_required": (
            "Я попытался найти подтверждённые цифры по этой теме, но не смог собрать достаточно надёжный factual context.\n"
            "Чтобы не выдумывать факты, я не буду генерировать такой пост вслепую.\n\n"
            "Что можно сделать:\n"
            "• пришли проверенные цифры или выдержку из источника, и я упакую их в пост\n"
            "• или попробуй уточнить запрос, например добавить рынок, страну, модель и год"
        ),
        "free_limit_reached": (
            "<blockquote>⌁ Бесплатный лимит закончился. Дальше доступ открывается через Telegram Stars.</blockquote>\n\n"
            "◦ 14 days — <code>{price14} ⭐</code>\n"
            "◦ 30 days — <code>{price30} ⭐</code>\n"
            "◦ 90 days — <code>{price90} ⭐</code>"
        ),
        "free_cooldown_wait": "Для защиты от абуза бесплатные генерации идут с паузой. Подожди ещё <code>{seconds}</code> сек.",
        "connect_limit_reached": (
            "На бесплатном режиме можно полноценно работать только с ограниченным числом новых каналов.\n"
            "Лимит для этого аккаунта: <code>{limit}</code> уникальных каналов.\n"
            "Чтобы подключать ещё каналы без ограничений, нужен активный платный доступ."
        ),
        "photo_found_caption": (
            "<b>Подобрал фото для поста</b>\n"
            "Запрос: <code>{query}</code>\n"
            "{source}"
            "Автор: {author}"
        ),
        "photo_source_with_link": "Источник: <a href=\"{url}\">{provider}</a>\n",
        "photo_source_plain": "Источник: {provider}\n",
        "preview_title": "<b>Сгенерированный пост</b>\n<i>Формат публикации: {format}</i>\n<i>Контекст: {context}</i>\n\n{post_text}",
        "preview_context_full": "память о канале заполнена",
        "preview_context_empty": "память о канале почти пустая, лучше заполнить /profile",
        "preview_context_live_data": "подтянуты подтверждённые данные",
        "draft_not_found": "Черновик не найден.",
        "draft_not_yours": "Этот черновик создан другим пользователем.",
        "custom_photo_prompt": "Отправь свою фотографию одним сообщением, и я заменю текущую.",
        "custom_photo_saved": "Твоя фотография сохранена. Теперь при публикации я использую именно её.",
        "custom_photo_invalid": "Нужна именно фотография. Просто отправь фото одним сообщением.",
        "edit_text_prompt": "Отправь новый текст поста одним сообщением, и я заменю текущий черновик.",
        "edit_text_saved": "Текст черновика обновлён.",
        "edit_text_invalid": "Нужен именно текст одним сообщением.",
        "regenerate_started": "Перегенерирую этот же пост с новым углом и подачей...",
        "regenerate_done": "Готово. Обновил черновик новым вариантом.",
        "caption_trimmed_notice": "Чтобы фото и текст ушли одним сообщением, я аккуратно сократил текст под лимит caption Telegram.",
        "photo_refresh_failed": "Не удалось подобрать другое фото.",
        "photo_refresh_none": "Подходящих новых фото не нашёл.",
        "photo_refresh_ok": "Подобрал другое фото.",
        "publish_ok": "Пост опубликован.",
        "publish_success_message": "Пост успешно отправлен в канал.",
        "profile_required": "Сначала подключи канал через <code>/connect</code>, а потом уже настроим его профиль.",
        "profile_intro": (
            "Настроим память о канале. Я задам 6 коротких вопросов.\n"
            "Если хочешь пропустить пункт, отправь <code>-</code>.\n\n"
            "{summary}\n\n"
            "1. Какая основная тема канала?"
        ),
        "profile_empty": "Пока в памяти только пустой профиль канала.",
        "profile_saved": "Профиль канала сохранён. Теперь бот будет учитывать тему, аудиторию и образ автора.\n\n{summary}",
        "profile_summary_title": "<b>Текущая память о канале</b>",
        "profile_q2": "2. Кто основная аудитория канала?",
        "profile_q3": "3. Кто админ и как он должен звучать в постах?",
        "profile_q4": "4. Какие темы или рубрики обычно выходят в канале? Можно перечислить через запятую.",
        "profile_q5": "5. Какой стиль нужен? Например: дерзкий, экспертный, дружелюбный, ироничный, без воды.",
        "profile_q6": "6. Есть ли запреты или стоп-темы? Например: без политики, без агрессии, без кликбейта.",
        "buy_intro": "Бесплатно доступно {limit} генераций. Дальше можно открыть доступ через Telegram Stars.\n\nВыбери план:",
        "status_active": (
            "<b>Status</b>\n\n"
            "<blockquote>⌁ Подписка активна до <code>{expires}</code>.</blockquote>\n"
            "◦ Использовано бесплатных генераций: <code>{used}</code>"
        ),
        "status_inactive": (
            "<b>Status</b>\n\n"
            "<blockquote>⌁ Подписка сейчас не активна.</blockquote>\n"
            "◦ Осталось бесплатных генераций: <code>{left}</code> из <code>{limit}</code>\n\n"
            "↳ Открыть доступ: <code>/buy</code>"
        ),
        "terms": (
            "<b>Terms</b>\n\n"
            "<blockquote>⌁ Бот даёт ограниченное количество бесплатных генераций, а дальше открывается по подписке.</blockquote>\n\n"
            "◦ доступ после оплаты идёт через Telegram Stars\n"
            "◦ покупка даёт доступ на выбранный срок\n"
            "◦ возвраты работают только в поддерживаемых Telegram refund-сценариях\n"
            "◦ анти-абузные ограничения могут включать cooldown, лимит каналов и suspicious flags"
        ),
        "privacy": (
            "<b>Privacy</b>\n\n"
            "<blockquote>⌁ Бот хранит рабочий контекст только для того, чтобы писать ближе к реальному стилю канала.</blockquote>\n\n"
            "◦ хранится подключённый канал, память о канале и черновики\n"
            "◦ личный Groq API key хранится в зашифрованном виде\n"
            "◦ бот использует сторонние API: Groq, Pexels, Pixabay, CoinGecko\n"
            "◦ платежи идут через Telegram Stars\n"
            "◦ для качества текста могут использоваться реальные посты канала, собранные через channel_post или через <code>/teach</code>"
        ),
        "pay_support": "Если возникла проблема с оплатой, напиши владельцу бота и приложи дату покупки или чек Telegram.",
        "reset_all_warning": (
            "<b>Полный сброс</b>\n\n"
            "Я удалю рабочее состояние:\n"
            "• подключённый канал\n"
            "• память о канале\n"
            "• черновики\n"
            "• сохранённый AI-ключ\n"
            "• локальные настройки этого рабочего пространства\n\n"
            "Я НЕ сброшу:\n"
            "• бесплатные лимиты\n"
            "• оплаченный доступ\n"
            "• анти-абузную историю подключённых каналов\n\n"
            "Деньги Telegram Stars это не возвращает.\n\n"
            "Если действительно хочешь начать с нуля, отправь одним сообщением <code>СБРОС</code>."
        ),
        "reset_all_cancelled": "Сброс отменён.",
        "reset_all_done": "Готово. Рабочее пространство очищено: можешь заново пройти <code>/start</code>, <code>/ai</code> и <code>/connect</code>. Бесплатные лимиты и подписка при этом сохранены.",
        "unknown_plan": "Неизвестный тариф.",
        "invoice_description": "Доступ к AI Shadow Writer на {duration}.",
        "plan_unavailable": "Этот тариф больше недоступен.",
        "payment_unrecognized": "Платёж получен, но тариф не распознан. Напиши в поддержку бота.",
        "payment_success": "Оплата получена ✅\nТариф: <code>{title}</code>\nДоступ открыт до <code>{expires}</code>.\n\nТеперь можно снова использовать /post.",
        "error_generic_message": "Что-то пошло не так. Я уже записал ошибку в логи. Попробуй ещё раз через пару секунд.",
        "error_generic_callback": "Что-то пошло не так. Попробуй ещё раз.",
        "photo_label_custom": "твоя фотография",
        "photo_label_provider": "фото из {provider}",
        "photo_label_none": "без фото",
        "sticker_label": "стикер",
        "publish_button": "Опубликовать",
        "edit_text_button": "Изменить текст",
        "regenerate_button": "Перегенерировать",
        "refresh_photo_button": "Другое фото",
        "upload_photo_button": "Своя фотка",
        "show_sources_button": "Показать источники",
        "sources_title": "<b>Источники и цифры</b>",
        "sources_empty": "Для этого черновика источники не сохранены.",
        "sources_block": "<b>{title}</b>\n{url}\n{facts}",
        "buy_14_button": "14 дней • {price} ⭐",
        "buy_30_button": "30 дней • {price} ⭐",
        "buy_90_button": "90 дней • {price} ⭐",
        "sticker_debug_message": (
            "<b>Sticker debug</b>\n"
            "file_id:\n<code>{file_id}</code>\n\n"
            "file_unique_id:\n<code>{file_unique_id}</code>"
        ),
        "animation_debug_message": (
            "<b>Animation debug</b>\n"
            "file_id:\n<code>{file_id}</code>\n\n"
            "file_unique_id:\n<code>{file_unique_id}</code>"
        ),
        "video_debug_message": (
            "<b>Video debug</b>\n"
            "file_id:\n<code>{file_id}</code>\n\n"
            "file_unique_id:\n<code>{file_unique_id}</code>"
        ),
        "admin_denied": "Эта панель доступна только владельцу бота.",
        "admin_panel_message": (
            "<b>Admin Panel</b>\n\n"
            "<b>Тарифы и лимиты</b>\n"
            "• Free limit: <code>{free_limit}</code>\n"
            "• Cooldown: <code>{cooldown}</code> sec\n"
            "• Free unique channels: <code>{unique_channels}</code>\n"
            "• 14 days: <code>{price_14} ⭐</code>\n"
            "• 30 days: <code>{price_30} ⭐</code>\n"
            "• 90 days: <code>{price_90} ⭐</code>\n\n"
            "<b>Abuse monitor</b>\n"
            "• Flagged users: <code>{suspicious_total}</code>\n"
            "{recent_flags}\n\n"
            "<b>Analytics</b>\n"
            "• /start: <code>{start_total}</code>\n"
            "• /ai opened: <code>{ai_opened}</code>\n"
            "• AI connected: <code>{ai_connected}</code>\n"
            "• AI validation failed: <code>{ai_failed}</code>\n"
            "• Channel connected: <code>{channel_connected}</code>\n"
            "• Connect rejected: <code>{connect_rejected}</code>\n"
            "• Post attempts: <code>{post_attempt}</code>\n"
            "• Posts succeeded: <code>{post_success}</code>\n"
            "• Posts failed (no AI): <code>{post_failed_no_ai}</code>\n"
            "• Posts failed (Groq): <code>{post_failed_groq}</code>\n"
            "• Payments: <code>{payment_success}</code>\n"
            "• Unhandled errors: <code>{unhandled_error}</code>\n\n"
            "<b>Брендинг</b>\n"
            "• Welcome GIF: <code>{animation_id}</code>\n"
            "• Welcome sticker: <code>{sticker_id}</code>\n\n"
            "<b>Тексты</b>\n"
            "• About RU: <code>{about_ru}</code>\n"
            "• About EN: <code>{about_en}</code>\n\n"
            "<i>Нажми кнопку ниже и пришли новое значение.</i>"
        ),
        "admin_set_prompt": "Меняем <b>{setting}</b>.\n\n{hint}",
        "admin_saved": "Сохранил: <b>{setting}</b>.",
        "admin_invalid_value": "Пришли значение одним сообщением.",
        "admin_number_required": "Тут нужно прислать целое число 0 или больше.",
        "admin_unexpected_media": "Для этого поля сейчас нужен другой тип сообщения.",
        "admin_value_set": "задано",
        "admin_value_empty": "пусто",
        "admin_price_14_button": "Цена 14 дн",
        "admin_price_30_button": "Цена 30 дн",
        "admin_price_90_button": "Цена 90 дн",
        "admin_free_limit_button": "Free limit",
        "admin_cooldown_button": "Cooldown",
        "admin_unique_channels_button": "Free channels",
        "admin_animation_button": "Welcome GIF",
        "admin_sticker_button": "Welcome sticker",
        "admin_about_ru_button": "About RU",
        "admin_about_en_button": "About EN",
        "admin_refresh_button": "Обновить",
        "admin_hint_free_posts_limit": "Отправь новое число бесплатных генераций, например <code>5</code>.",
        "admin_hint_free_generation_cooldown_seconds": "Отправь cooldown между бесплатными генерациями в секундах, например <code>90</code>.",
        "admin_hint_max_unique_channels_free": "Отправь число уникальных каналов, доступных на free-tier, например <code>3</code>.",
        "admin_hint_stars_price_14_days": "Отправь цену тарифа на 14 дней в Stars.",
        "admin_hint_stars_price_30_days": "Отправь цену тарифа на 30 дней в Stars.",
        "admin_hint_stars_price_90_days": "Отправь цену тарифа на 90 дней в Stars.",
        "admin_hint_brand_animation_id": "Пришли GIF/animation одним сообщением. Я сам возьму <code>file_id</code>.",
        "admin_hint_brand_sticker_id": "Пришли стикер одним сообщением. Я сам возьму <code>file_id</code>.",
        "admin_hint_about_text_ru": "Пришли новый HTML-текст для <code>/about</code> на русском.",
        "admin_hint_about_text_en": "Send the new HTML text for <code>/about</code> in English.",
        "admin_flags_empty": "• No suspicious users",
        "admin_flag_line": "• user <code>{user_id}</code> — {reason}",
    },
    "en": {
        "start_message": (
            "<b>AI Shadow Writer</b>\n"
            "<i>Telegram channel writing system</i>\n\n"
            "<blockquote>⌁ Turns raw ideas into channel-ready drafts that feel authored, not mechanically generated.</blockquote>\n\n"
            "<b>◦ Inside</b>\n"
            "◦ connect your own AI key via <code>/ai</code>\n"
            "◦ channel memory and author voice\n"
            "◦ photo search, replacement, and publishing\n"
            "◦ English / Russian workflow\n"
            "◦ limits and Telegram Stars access\n\n"
            "<b>◦ Quick start</b>\n"
            "1. <code>/ai</code>\n"
            "2. <code>/connect</code>\n"
            "3. <code>/profile</code>\n"
            "4. <code>/post your idea</code>\n\n"
            "<i>⌁ The menu below is ready for faster navigation.</i>"
        ),
        "help_message": (
            "<b>Command Center</b>\n\n"
            "<blockquote>⌁ Everything below affects the bot interface only. Generated post drafts keep their own style.</blockquote>\n\n"
            "<b>◦ Setup</b>\n"
            "◦ <code>/ai</code> — connect your personal Groq API key\n"
            "◦ <code>/groq_help</code> — where to get a Groq API key\n"
            "◦ <code>/ai_status</code> — show current AI connection\n"
            "◦ <code>/ai_disconnect</code> — remove your AI key\n"
            "◦ <code>/connect</code> — connect a channel\n"
            "◦ <code>/teach</code> — add real channel post samples\n"
            "◦ <code>/profile</code> — fill channel memory\n"
            "◦ <code>/profile_show</code> — show saved profile\n\n"
            "<b>◦ Content</b>\n"
            "◦ <code>/post &lt;idea&gt;</code> — generate a post draft\n"
            "◦ use the buttons under a draft to edit text, regenerate, or swap the photo\n\n"
            "<b>◦ Access</b>\n"
            "◦ <code>/status</code> — usage and subscription\n"
            "◦ <code>/buy</code> — unlock access with Stars\n"
            "◦ paid access is handled through Telegram Stars\n\n"
            "<b>◦ Info</b>\n"
            "◦ <code>/about</code> — about the bot\n"
            "◦ <code>/contacts</code> — creator contacts and links\n"
            "◦ <code>/language ru|en</code> — interface + post language\n"
            "◦ <code>/terms</code> — terms\n"
            "◦ <code>/privacy</code> — privacy and storage\n"
            "◦ <code>/paysupport</code> — payment support"
        ),
        "setup_message": (
            "<b>Setup Guide</b>\n\n"
            "<blockquote>⌁ Before the bot can publish to your channel, it must be added to that channel as an admin with posting rights.</blockquote>\n\n"
            "<b>◦ Step by step</b>\n"
            "1. Add the bot to your Telegram channel as an admin\n"
            "2. Make sure it has permission to publish posts\n"
            "3. Open <code>/groq_help</code> and create your Groq API key\n"
            "4. Send <code>/ai</code> and connect that key\n"
            "5. Send <code>/connect</code> and forward any post from the channel, or send the channel ID manually\n"
            "6. Fill in <code>/profile</code> so the bot understands the channel voice\n"
            "7. Optionally use <code>/teach</code> and forward 3-10 older posts from the same channel\n"
            "8. Generate a draft with <code>/post your idea</code>\n"
            "9. Review the draft, adjust text or photo, then publish\n\n"
            "<b>◦ Important</b>\n"
            "◦ no admin rights = no publishing\n"
            "◦ no Groq key = no generation\n"
            "◦ no connected channel = nowhere to publish"
        ),
        "faq_message": (
            "<b>FAQ</b>\n\n"
            "<blockquote>⌁ If something looks broken, most often it is one of the setup conditions below.</blockquote>\n\n"
            "<b>◦ Why can't the bot publish to my channel?</b>\n"
            "◦ the bot was not added as an admin\n"
            "◦ or it does not have permission to publish posts\n\n"
            "<b>◦ Why does /post not work?</b>\n"
            "◦ your personal Groq API key is not connected yet\n"
            "◦ use <code>/groq_help</code> then <code>/ai</code>\n\n"
            "<b>◦ Why does /connect fail?</b>\n"
            "◦ the forwarded post may hide channel metadata\n"
            "◦ try forwarding another post or send the channel ID manually\n\n"
            "<b>◦ Why is the style weak or generic?</b>\n"
            "◦ fill in <code>/profile</code>\n"
            "◦ then use <code>/teach</code> with real older channel posts\n\n"
            "<b>◦ Why is the photo wrong?</b>\n"
            "◦ use the buttons under the draft to swap the photo or upload your own\n\n"
            "<b>◦ Why does the bot answer in the wrong language?</b>\n"
            "◦ switch it with <code>/language en</code> or <code>/language ru</code>"
        ),
        "about_message": (
            "<b>About AI Shadow Writer</b>\n\n"
            "<blockquote>⌁ An MVP system for Telegram channel admins who need a cleaner AI writing workflow with channel memory, visuals, and fast publishing.</blockquote>\n\n"
            "<b>◦ How it works</b>\n"
            "◦ the bot subscription pays for the product itself\n"
            "◦ generation runs through each user's own AI key\n"
            "◦ the bot keeps channel context to speed up publishing\n\n"
            "<b>◦ Core strengths</b>\n"
            "◦ channel-aware writing instead of generic AI output\n"
            "◦ visual support and photo replacement\n"
            "◦ bilingual workflow in EN / RU\n"
            "◦ Telegram Stars access model\n\n"
            "<b>◦ Author</b>\n"
            "Tenyokj · Shadow Writer AI"
        ),
        "contacts_message": (
            "<b>Creator Contacts</b>\n\n"
            "<blockquote>⌁ Reach out for launch questions, bugs, ideas, or collaboration.</blockquote>\n\n"
            "◦ Email: <a href=\"mailto:dv842449@gmail.com\">dv842449@gmail.com</a>\n"
            "◦ Telegram: <a href=\"https://t.me/tenkoffj\">@tenkoffj</a>\n"
            "◦ GitHub: <a href=\"https://github.com/Tenyokj\">Tenyokj</a>\n"
            "◦ Website: <a href=\"https://tenyokj.vercel.app/\">tenyokj.vercel.app</a>\n\n"
            "<i>⌁ Telegram is the fastest way to reach me.</i>"
        ),
        "language_set_ru": "Язык переключён на русский. Теперь и интерфейс, и посты будут на русском.",
        "language_set_en": "Language switched to English. Now both the interface and generated posts will be in English.",
        "language_usage": "Use <code>/language ru</code> or <code>/language en</code>.",
        "cancel_done": "⌁ The current mode was cleared. We can continue from a clean state.",
        "ai_intro": (
            "<b>Connect AI</b>\n\n"
            "1. Create an API key in Groq\n"
            "2. Send it here in the next message\n"
            "3. I will encrypt it and use it only for your generations\n\n"
            "Current default model: <code>{model}</code>"
        ),
        "groq_help_message": (
            "<b>Groq API Key Guide</b>\n\n"
            "<blockquote>⌁ You only need to do this once. After that, the bot will use your own Groq API key for generation.</blockquote>\n\n"
            "<b>◦ Steps</b>\n"
            "1. Open <a href=\"https://console.groq.com/keys\">console.groq.com/keys</a>\n"
            "2. Sign in or create an account\n"
            "3. Create a new API key\n"
            "4. Copy the key\n"
            "5. Come back here and send <code>/ai</code>\n"
            "6. Paste the key in the next message\n\n"
            "<b>◦ Notes</b>\n"
            "◦ the key is stored in encrypted form\n"
            "◦ the bot uses your own Groq limits\n"
            "◦ once you send me your tutorial video, I can attach it to this command"
        ),
        "ai_validating": "Validating your Groq key...",
        "ai_connected": "AI key connected ✅\nNow /post will run through your Groq key.\nModel: <code>{model}</code>",
        "ai_status_empty": "No personal AI key is connected yet.\nUse <code>/ai</code>.\nDefault model: <code>{model}</code>",
        "ai_status_connected": "AI is connected ✅\nProvider: <code>{provider}</code>\nModel: <code>{model}</code>",
        "ai_disconnected": "Your personal AI key has been removed. If there is no global server key, /post will ask you to run <code>/ai</code> again.",
        "ai_required": "First connect your AI key via <code>/ai</code>. Without it I can't generate posts.",
        "ai_storage_not_ready": "Secure key storage is not configured on the server yet. The owner needs to set <code>MASTER_ENCRYPTION_KEY</code>.",
        "ai_key_invalid": "Send only the API key in one message, with no command and no extra text.",
        "ai_key_check_failed": "I couldn't validate this Groq key.\nTechnical error: <code>{error}</code>",
        "ai_key_broken": "I couldn't decrypt or read your saved AI key. Please reconnect it via <code>/ai</code>.",
        "connect_prompt": (
            "<b>Connect Channel</b>\n\n"
            "<blockquote>⌁ Forward any post from your channel and I'll try to detect the channel ID automatically.</blockquote>\n\n"
            "◦ you can also send the ID manually: <code>-1001234567890</code>\n"
            "◦ add the bot to the channel first\n"
            "◦ grant it permission to publish"
        ),
        "teach_intro": (
            "Now you can teach the bot using real older posts from the channel.\n"
            "Forward 3-10 older posts from the currently connected channel here.\n"
            "When you are done, send <code>/done</code>. If you changed your mind, send <code>/cancel</code>."
        ),
        "teach_invalid": "You are still in /teach mode. I need a forwarded post from the currently connected channel with non-empty text. To exit, use <code>/done</code> or <code>/cancel</code>.",
        "teach_saved_one": "Saved one sample post. Added so far: <code>{count}</code>.",
        "teach_done": "Done. Saved samples: <code>{count}</code>. Generation should now feel closer to the real channel voice.",
        "connect_success": (
            "Channel <code>{channel_id}</code> connected. Now you can use "
            "<code>/post post idea</code>.\n"
            "To make the bot sound more like the real author, also fill in <code>/profile</code>."
        ),
        "connect_success_switched": (
            "New channel <code>{channel_id}</code> connected.\n"
            "I reset the previous channel memory so it does not leak into this one.\n"
            "Now fill in <code>/profile</code> again for the new channel.\n\n"
            "Your limits, subscription, and AI key are kept as-is. For a full clean restart use <code>/reset_all</code>."
        ),
        "connect_success_reused": (
            "Channel <code>{channel_id}</code> has been connected again.\n"
            "I keep a record that this channel was already used by this account, so free limits and billing status do not restart from zero.\n"
            "If needed, just fill in <code>/profile</code> again for this channel."
        ),
        "connect_waiting": "I'm waiting for either a forwarded post from the channel or the channel ID in the format <code>-1001234567890</code>.",
        "connect_forward_missing_metadata": (
            "Telegram did not include channel metadata in this forwarded message.\n"
            "This can happen if the channel has protected content enabled or the forward arrived without origin details.\n\n"
            "What you can do:\n"
            "• send the channel ID manually in the format <code>-1001234567890</code>\n"
            "• or forward another post from the same channel\n"
            "• and make sure the bot is added to the channel as an admin"
        ),
        "connect_invalid": "That doesn't look like a valid channel ID. Example: <code>-1001234567890</code>.",
        "channel_required": "First connect a channel via <code>/connect</code> so I know where to publish.",
        "post_usage": "Use this format: <code>/post your post idea</code>.",
        "post_generating": "Generating a channel-style post, this will take a few seconds...",
        "post_fetching_market_data": "Pulling live market data so the post uses exact numbers...",
        "post_fetching_web_facts": "Searching the web for verified facts and figures...",
        "post_error": "Couldn't get a response from Groq API. Check your key and model settings.\nTechnical error: <code>{error}</code>",
        "post_live_data_error": "I couldn't fetch current market data.\nWithout it, I won't invent numbers.\nTechnical error: <code>{error}</code>",
        "post_fact_mode_required": (
            "I tried to find verified figures for this topic, but I could not build a reliable enough factual context.\n"
            "To avoid inventing facts, I won't generate this kind of post blindly.\n\n"
            "What you can do:\n"
            "• send verified figures or a source excerpt, and I will turn it into a post\n"
            "• or make the request more specific, for example by adding the market, country, model, and year"
        ),
        "free_limit_reached": (
            "<blockquote>⌁ Your free limit is over. To continue, unlock access with Telegram Stars.</blockquote>\n\n"
            "◦ 14 days — <code>{price14} ⭐</code>\n"
            "◦ 30 days — <code>{price30} ⭐</code>\n"
            "◦ 90 days — <code>{price90} ⭐</code>"
        ),
        "free_cooldown_wait": "To prevent abuse, free generations have a pause between them. Please wait <code>{seconds}</code> more seconds.",
        "connect_limit_reached": (
            "In free mode, each account can fully work only with a limited number of new channels.\n"
            "Your current limit is <code>{limit}</code> unique channels.\n"
            "To connect more channels without restrictions, activate a paid plan."
        ),
        "photo_found_caption": (
            "<b>Found a photo for the post</b>\n"
            "Query: <code>{query}</code>\n"
            "{source}"
            "Author: {author}"
        ),
        "photo_source_with_link": "Source: <a href=\"{url}\">{provider}</a>\n",
        "photo_source_plain": "Source: {provider}\n",
        "preview_title": "<b>Generated Post</b>\n<i>Publishing format: {format}</i>\n<i>Context: {context}</i>\n\n{post_text}",
        "preview_context_full": "channel memory is filled in",
        "preview_context_empty": "channel memory is still sparse, better fill in /profile",
        "preview_context_live_data": "verified data included",
        "draft_not_found": "Draft not found.",
        "draft_not_yours": "This draft belongs to another user.",
        "custom_photo_prompt": "Send your own photo in one message and I'll replace the current one.",
        "custom_photo_saved": "Your photo is saved. I will use it when publishing.",
        "custom_photo_invalid": "I need an actual photo. Just send an image in one message.",
        "edit_text_prompt": "Send the new post text in one message and I will replace the current draft.",
        "edit_text_saved": "The draft text was updated.",
        "edit_text_invalid": "I need plain text in one message.",
        "regenerate_started": "Regenerating the same post with a new angle and style...",
        "regenerate_done": "Done. I updated the draft with a new version.",
        "caption_trimmed_notice": "To keep the photo and text in one Telegram message, I shortened the text to fit the caption limit.",
        "photo_refresh_failed": "Couldn't find a better replacement photo.",
        "photo_refresh_none": "I couldn't find a good alternative photo.",
        "photo_refresh_ok": "Found another photo.",
        "publish_ok": "Post published.",
        "publish_success_message": "The post was successfully sent to the channel.",
        "profile_required": "First connect a channel via <code>/connect</code>, then we can configure its profile.",
        "profile_intro": (
            "Let's set up channel memory. I'll ask 6 short questions.\n"
            "If you want to skip a field, send <code>-</code>.\n\n"
            "{summary}\n\n"
            "1. What is the main topic of the channel?"
        ),
        "profile_empty": "The channel memory is still mostly empty.",
        "profile_saved": "Channel profile saved. From now on the bot will use the topic, audience, and author persona.\n\n{summary}",
        "profile_summary_title": "<b>Current Channel Memory</b>",
        "profile_q2": "2. Who is the main audience of the channel?",
        "profile_q3": "3. Who is the admin and how should they sound in posts?",
        "profile_q4": "4. What topics or recurring content pillars usually appear in the channel? You can separate them with commas.",
        "profile_q5": "5. What style should the writing have? For example: bold, expert, friendly, ironic, concise.",
        "profile_q6": "6. Any forbidden or unwanted topics? For example: no politics, no aggression, no clickbait.",
        "buy_intro": "You get {limit} free generations. After that, unlock access with Telegram Stars.\n\nChoose a plan:",
        "status_active": (
            "<b>Status</b>\n\n"
            "<blockquote>⌁ Subscription is active until <code>{expires}</code>.</blockquote>\n"
            "◦ Free generations already used: <code>{used}</code>"
        ),
        "status_inactive": (
            "<b>Status</b>\n\n"
            "<blockquote>⌁ Subscription is not active right now.</blockquote>\n"
            "◦ Free generations left: <code>{left}</code> out of <code>{limit}</code>\n\n"
            "↳ Unlock access: <code>/buy</code>"
        ),
        "terms": (
            "<b>Terms</b>\n\n"
            "<blockquote>⌁ The bot provides a limited number of free generations, then unlocks through subscription access.</blockquote>\n\n"
            "◦ access after that is handled via Telegram Stars\n"
            "◦ a purchase unlocks the selected period\n"
            "◦ refunds depend on supported Telegram refund flows\n"
            "◦ anti-abuse limits may include cooldowns, channel caps, and suspicious activity flags"
        ),
        "privacy": (
            "<b>Privacy</b>\n\n"
            "<blockquote>⌁ The bot keeps working context only to write closer to the real style of your channel.</blockquote>\n\n"
            "◦ it stores the connected channel, channel memory, and working drafts\n"
            "◦ your personal Groq API key is stored in encrypted form\n"
            "◦ the bot uses third-party APIs: Groq, Pexels, Pixabay, and CoinGecko\n"
            "◦ payments are handled through Telegram Stars\n"
            "◦ to improve writing quality, the bot may use real channel posts collected via channel_post updates or posts you forward with <code>/teach</code>"
        ),
        "pay_support": "If you have a payment issue, contact the bot owner and include the purchase date or Telegram receipt.",
        "reset_all_warning": (
            "<b>Full Reset</b>\n\n"
            "I will delete your working state:\n"
            "• connected channel\n"
            "• channel memory\n"
            "• drafts\n"
            "• saved AI key\n"
            "• local workspace settings\n\n"
            "I will NOT reset:\n"
            "• free limits\n"
            "• paid access\n"
            "• anti-abuse history of connected channels\n\n"
            "This does not refund Telegram Stars.\n\n"
            "If you really want to start from zero, send <code>RESET</code> in one message."
        ),
        "reset_all_cancelled": "Reset cancelled.",
        "reset_all_done": "Done. The workspace has been cleared: you can go through <code>/start</code>, <code>/ai</code>, and <code>/connect</code> again. Your free limits and subscription were preserved.",
        "unknown_plan": "Unknown plan.",
        "invoice_description": "AI Shadow Writer access for {duration}.",
        "plan_unavailable": "This plan is no longer available.",
        "payment_unrecognized": "Payment received, but the plan could not be recognized. Please contact support.",
        "payment_success": "Payment received ✅\nPlan: <code>{title}</code>\nAccess is active until <code>{expires}</code>.\n\nYou can now use /post again.",
        "error_generic_message": "Something went wrong. I logged the error. Please try again in a few seconds.",
        "error_generic_callback": "Something went wrong. Please try again.",
        "photo_label_custom": "your photo",
        "photo_label_provider": "photo from {provider}",
        "photo_label_none": "no photo",
        "sticker_label": "sticker",
        "publish_button": "Publish",
        "edit_text_button": "Edit text",
        "regenerate_button": "Regenerate",
        "refresh_photo_button": "Another photo",
        "upload_photo_button": "My own photo",
        "show_sources_button": "Show sources",
        "sources_title": "<b>Sources and figures</b>",
        "sources_empty": "No saved sources were found for this draft.",
        "sources_block": "<b>{title}</b>\n{url}\n{facts}",
        "buy_14_button": "14 days • {price} ⭐",
        "buy_30_button": "30 days • {price} ⭐",
        "buy_90_button": "90 days • {price} ⭐",
        "sticker_debug_message": (
            "<b>Sticker debug</b>\n"
            "file_id:\n<code>{file_id}</code>\n\n"
            "file_unique_id:\n<code>{file_unique_id}</code>"
        ),
        "animation_debug_message": (
            "<b>Animation debug</b>\n"
            "file_id:\n<code>{file_id}</code>\n\n"
            "file_unique_id:\n<code>{file_unique_id}</code>"
        ),
        "video_debug_message": (
            "<b>Video debug</b>\n"
            "file_id:\n<code>{file_id}</code>\n\n"
            "file_unique_id:\n<code>{file_unique_id}</code>"
        ),
        "admin_denied": "This panel is available only to the bot owner.",
        "admin_panel_message": (
            "<b>Admin Panel</b>\n\n"
            "<b>Pricing and limits</b>\n"
            "• Free limit: <code>{free_limit}</code>\n"
            "• Cooldown: <code>{cooldown}</code> sec\n"
            "• Free unique channels: <code>{unique_channels}</code>\n"
            "• 14 days: <code>{price_14} ⭐</code>\n"
            "• 30 days: <code>{price_30} ⭐</code>\n"
            "• 90 days: <code>{price_90} ⭐</code>\n\n"
            "<b>Abuse monitor</b>\n"
            "• Flagged users: <code>{suspicious_total}</code>\n"
            "{recent_flags}\n\n"
            "<b>Analytics</b>\n"
            "• /start: <code>{start_total}</code>\n"
            "• /ai opened: <code>{ai_opened}</code>\n"
            "• AI connected: <code>{ai_connected}</code>\n"
            "• AI validation failed: <code>{ai_failed}</code>\n"
            "• Channel connected: <code>{channel_connected}</code>\n"
            "• Connect rejected: <code>{connect_rejected}</code>\n"
            "• Post attempts: <code>{post_attempt}</code>\n"
            "• Posts succeeded: <code>{post_success}</code>\n"
            "• Posts failed (no AI): <code>{post_failed_no_ai}</code>\n"
            "• Posts failed (Groq): <code>{post_failed_groq}</code>\n"
            "• Payments: <code>{payment_success}</code>\n"
            "• Unhandled errors: <code>{unhandled_error}</code>\n\n"
            "<b>Branding</b>\n"
            "• Welcome GIF: <code>{animation_id}</code>\n"
            "• Welcome sticker: <code>{sticker_id}</code>\n\n"
            "<b>Texts</b>\n"
            "• About RU: <code>{about_ru}</code>\n"
            "• About EN: <code>{about_en}</code>\n\n"
            "<i>Tap a button below and send the new value.</i>"
        ),
        "admin_set_prompt": "Updating <b>{setting}</b>.\n\n{hint}",
        "admin_saved": "Saved: <b>{setting}</b>.",
        "admin_invalid_value": "Send the new value in one message.",
        "admin_number_required": "This field expects an integer equal to or above 0.",
        "admin_unexpected_media": "This field expects a different message type right now.",
        "admin_value_set": "set",
        "admin_value_empty": "empty",
        "admin_price_14_button": "14d price",
        "admin_price_30_button": "30d price",
        "admin_price_90_button": "90d price",
        "admin_free_limit_button": "Free limit",
        "admin_cooldown_button": "Cooldown",
        "admin_unique_channels_button": "Free channels",
        "admin_animation_button": "Welcome GIF",
        "admin_sticker_button": "Welcome sticker",
        "admin_about_ru_button": "About RU",
        "admin_about_en_button": "About EN",
        "admin_refresh_button": "Refresh",
        "admin_hint_free_posts_limit": "Send the new number of free generations, for example <code>5</code>.",
        "admin_hint_free_generation_cooldown_seconds": "Send the cooldown between free generations in seconds, for example <code>90</code>.",
        "admin_hint_max_unique_channels_free": "Send the number of unique channels allowed on the free tier, for example <code>3</code>.",
        "admin_hint_stars_price_14_days": "Send the 14-day plan price in Stars.",
        "admin_hint_stars_price_30_days": "Send the 30-day plan price in Stars.",
        "admin_hint_stars_price_90_days": "Send the 90-day plan price in Stars.",
        "admin_hint_brand_animation_id": "Send a GIF/animation in one message. I will extract the <code>file_id</code> automatically.",
        "admin_hint_brand_sticker_id": "Send a sticker in one message. I will extract the <code>file_id</code> automatically.",
        "admin_hint_about_text_ru": "Send the new HTML text for <code>/about</code> in Russian.",
        "admin_hint_about_text_en": "Send the new HTML text for <code>/about</code> in English.",
        "admin_flags_empty": "• No suspicious users",
        "admin_flag_line": "• user <code>{user_id}</code> — {reason}",
    },
}


def normalize_language(language_code: str | None) -> str:
    if language_code in SUPPORTED_LANGUAGES:
        return str(language_code)
    return DEFAULT_LANGUAGE


def t(language_code: str | None, key: str, **kwargs: Any) -> str:
    lang = normalize_language(language_code)
    template = TEXTS[lang][key]
    return template.format(**kwargs)
