# AI Shadow Writer Bot

AI Shadow Writer is a Telegram bot for generating, refining, and publishing channel posts.

## Features

- `/start` — welcome message and product overview
- `/help` — all commands in one place
- `/setup` — first-time setup guide
- `/faq` — common issues and quick fixes
- `/about` — bot overview
- `/admin` — admin panel for pricing and branding
- `/groq_help` — step-by-step Groq API key guide
- `/teach` — upload real channel post samples via forwarded messages
- `/privacy` — short privacy and third-party API disclosure
- `/language ru|en` — switch interface and generation language
- `/connect` — connect a Telegram channel via a forwarded post or `channel_id`
- `/profile` — fill channel memory: topic, audience, author persona, pillars, style
- `/profile_show` — view the saved channel profile
- `/buy` — unlock access with Telegram Stars
- `/status` — check free usage and subscription status
- `/post &lt;idea&gt;` — generate a richer post draft through Groq
- automatic emoji placement inside AI-generated post drafts
- automatic photo lookup from Pexels and Pixabay
- replace the found photo with another one
- upload your own photo for a specific draft
- commands are registered automatically and appear in the Telegram slash menu
- optional sticker publishing if sticker `file_id` values are configured
- inline `Publish` button to send the approved post to the connected channel

## Installation

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then open `.env` and set:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
APP_ENV=dev
DATABASE_URL=
GROQ_API_KEY=your_groq_api_key
MASTER_ENCRYPTION_KEY=your_fernet_key
PIXABAY_API_KEY=your_pixabay_api_key
PEXELS_API_KEY=your_pexels_api_key
GROQ_MODEL=llama-3.3-70b-versatile
FREE_POSTS_LIMIT=5
FREE_GENERATION_COOLDOWN_SECONDS=90
MAX_UNIQUE_CHANNELS_FREE=3
STARS_PRICE_14_DAYS=25
STARS_PRICE_30_DAYS=40
STARS_PRICE_90_DAYS=100
GROQ_TUTORIAL_VIDEO_ID=

# Optional sticker file_id values for different publication moods
STICKER_FIRE_ID=
STICKER_IDEA_ID=
STICKER_NEWS_ID=
STICKER_WOW_ID=
BRAND_STICKER_ID=
BRAND_ANIMATION_ID=
ADMIN_USER_ID=123456789
```

Generate `MASTER_ENCRYPTION_KEY` with:

```bash
.venv/bin/python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Run

```bash
.venv/bin/python main.py
```

## Important Notes

- The bot must be added to the target channel as an administrator.
- The bot must have permission to publish posts in that channel.
- After `/connect`, it is highly recommended to complete `/profile` once so the bot writes in the voice of that specific channel instead of sounding generic.
- If `DATABASE_URL` is not set, the app uses the local SQLite file `shadow_writer.db`.
- If `DATABASE_URL` is set, the app uses PostgreSQL and ignores local SQLite.
- Use `APP_ENV=prod` for production so development and production environments do not get mixed up.
- If `PEXELS_API_KEY` is set, photo search will use Pexels first.
- If the selected photo is not good enough, use `Another photo` or upload your own image.
- After `FREE_POSTS_LIMIT` free generations, the bot asks for Telegram Stars payment.
- You can add a cooldown between free generations with `FREE_GENERATION_COOLDOWN_SECONDS`.
- You can limit how many unique channels a free-tier account can connect with `MAX_UNIQUE_CHANNELS_FREE`.
- If `BRAND_STICKER_ID` is set, the bot sends a branded sticker in `/start`.
- If `BRAND_ANIMATION_ID` is set, the bot sends a branded GIF or animation in `/start`.
- If `GROQ_TUTORIAL_VIDEO_ID` is set, the bot can show a Groq setup tutorial video in `/groq_help`.
- `ADMIN_USER_ID` is the Telegram user ID of the bot owner who can access `/admin`.
- Users can connect their own Groq API key through `/ai`, and generation will run on their personal Groq limits.
- `MASTER_ENCRYPTION_KEY` is required for secure encrypted storage of user AI keys. It must be a valid Fernet key.
- To improve writing quality, the bot stores real channel samples from `channel_post` updates and forwarded posts sent through `/teach`.

## SQLite Backup

Create a backup of the local SQLite database:

```bash
.venv/bin/python scripts/backup_sqlite.py
```

If the project already runs on PostgreSQL through `DATABASE_URL`, this script is not used. For production PostgreSQL, use your provider's backup tools.

## License

This project is proprietary. See [LICENSE](LICENSE).
