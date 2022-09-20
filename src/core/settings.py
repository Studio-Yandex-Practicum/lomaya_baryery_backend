import os
from pathlib import Path

from pydantic import BaseSettings, PostgresDsn
from pydantic.tools import lru_cache

BASE_DIR = Path(__file__).resolve().parent.parent.parent


if os.path.exists(str(BASE_DIR / ".env")):
    ENV_FILE = ".env"
else:
    ENV_FILE = ".env.example"


class Settings(BaseSettings):
    """Настройки проекта."""
    BOT_TOKEN: str
    DATABASE_URL: PostgresDsn
    BOT_WEBHOOK_MODE: bool = False
    BOT_WEBHOOK_PORT: int = 8443
    BOT_WEBHOOK_URL: str

    class Config:
        env_file = ENV_FILE


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

# Organization data
ORGANIZATIONS_EMAIL = 'info@stereotipov.net'
ORGANIZATIONS_GROUP = 'https://vk.com/socialrb02'
