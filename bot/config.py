import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "shadow_writer.db"
ENV_PATH = BASE_DIR / ".env"
DEFAULT_BOT_TOKEN = "TELEGRAM_BOT_TOKEN"
DEFAULT_GROQ_API_KEY = "GROQ_API_KEY"
DEFAULT_PIXABAY_API_KEY = "PIXABAY_API_KEY"
DEFAULT_MASTER_ENCRYPTION_KEY = "MASTER_ENCRYPTION_KEY"


def load_dotenv(env_path: Path) -> None:
    """
    Minimal .env loader without third-party dependencies.
    Existing environment variables are left unchanged.
    """
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", maxsplit=1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


load_dotenv(ENV_PATH)


@dataclass(slots=True)
class Settings:
    # Values can be supplied via environment variables such as
    # TELEGRAM_BOT_TOKEN and GROQ_API_KEY.
    bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", DEFAULT_BOT_TOKEN)
    app_env: str = os.getenv("APP_ENV", "dev").lower()
    database_url: str = os.getenv("DATABASE_URL", "").strip()
    webhook_base_url: str = os.getenv("WEBHOOK_BASE_URL", "").strip().rstrip("/")
    webhook_path: str = os.getenv("WEBHOOK_PATH", "/webhook").strip() or "/webhook"
    webhook_secret: str = os.getenv("WEBHOOK_SECRET", "").strip()
    web_server_host: str = os.getenv("WEB_SERVER_HOST", "0.0.0.0")
    web_server_port: int = int(os.getenv("PORT", os.getenv("WEB_SERVER_PORT", "8080")))
    groq_api_key: str = os.getenv("GROQ_API_KEY", DEFAULT_GROQ_API_KEY)
    master_encryption_key: str = os.getenv(
        "MASTER_ENCRYPTION_KEY",
        DEFAULT_MASTER_ENCRYPTION_KEY,
    )
    pixabay_api_key: str = os.getenv("PIXABAY_API_KEY", DEFAULT_PIXABAY_API_KEY)
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    groq_api_url: str = "https://api.groq.com/openai/v1/chat/completions"
    groq_models_api_url: str = "https://api.groq.com/openai/v1/models"
    pixabay_api_url: str = "https://pixabay.com/api/"
    pexels_api_key: str = os.getenv("PEXELS_API_KEY", "")
    pexels_api_url: str = "https://api.pexels.com/v1/search"
    coingecko_price_api_url: str = "https://api.coingecko.com/api/v3/simple/price"
    free_posts_limit: int = int(os.getenv("FREE_POSTS_LIMIT", "5"))
    free_generation_cooldown_seconds: int = int(
        os.getenv("FREE_GENERATION_COOLDOWN_SECONDS", "90")
    )
    max_unique_channels_free: int = int(
        os.getenv("MAX_UNIQUE_CHANNELS_FREE", "3")
    )
    stars_price_14_days: int = int(os.getenv("STARS_PRICE_14_DAYS", "25"))
    stars_price_30_days: int = int(os.getenv("STARS_PRICE_30_DAYS", "40"))
    stars_price_90_days: int = int(os.getenv("STARS_PRICE_90_DAYS", "100"))
    groq_tutorial_video_id: str = os.getenv("GROQ_TUTORIAL_VIDEO_ID", "")
    sticker_fire_id: str = os.getenv("STICKER_FIRE_ID", "")
    sticker_idea_id: str = os.getenv("STICKER_IDEA_ID", "")
    sticker_news_id: str = os.getenv("STICKER_NEWS_ID", "")
    sticker_wow_id: str = os.getenv("STICKER_WOW_ID", "")
    brand_sticker_id: str = os.getenv("BRAND_STICKER_ID", "")
    brand_animation_id: str = os.getenv("BRAND_ANIMATION_ID", "")
    admin_user_id: int = int(os.getenv("ADMIN_USER_ID", "0"))
    db_backup_dir: Path = BASE_DIR / "backups"

    @property
    def use_webhook(self) -> bool:
        return bool(self.webhook_base_url)

    @property
    def normalized_webhook_path(self) -> str:
        return self.webhook_path if self.webhook_path.startswith("/") else f"/{self.webhook_path}"

    @property
    def webhook_url(self) -> str:
        if not self.webhook_base_url:
            return ""
        return urljoin(f"{self.webhook_base_url}/", self.normalized_webhook_path.lstrip("/"))


settings = Settings()
