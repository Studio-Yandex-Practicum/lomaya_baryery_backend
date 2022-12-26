import os
from pathlib import Path

from pydantic import BaseSettings
from pydantic.tools import lru_cache

BASE_DIR = Path(__file__).resolve().parent.parent.parent

if os.path.exists(str(BASE_DIR / ".env")):
    ENV_FILE = ".env"
else:
    ENV_FILE = ".env.example"


class Settings(BaseSettings):
    """Настройки проекта."""

    BOT_TOKEN: str
    BOT_WEBHOOK_MODE: bool = False
    BOT_PERSISTENCE_FILE: str = str(BASE_DIR / "src" / "bot" / "bot_persistence_file")
    APPLICATION_URL: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    MIN_DAYS: int = 1
    MAX_DAYS: int = 93
    SEND_NEW_TASK_HOUR: int
    SEND_NO_REPORT_REMINDER_HOUR: int
    MIN_AGE: int
    HEALTHCHECK_API_URL: str
    DEBUG: bool = False
    SECRET_KEY: str

    # количество заданий для исключения участника из смены, на которое подряд не было отправлено отчетов
    SEQUENTIAL_TASKS_PASSES_FOR_EXCLUDE: int = 5

    @property
    def database_url(self):
        """Получить ссылку для подключения к DB."""
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def user_reports_dir(self):
        """Получить директорию для сохранения фотоотчета."""
        return BASE_DIR / 'data' / 'user_reports'

    @property
    def registration_template_url(self) -> str:
        """Получить ссылку для на HTML шаблон регистрации."""
        return f"{self.APPLICATION_URL}/static/registration.html"

    class Config:
        env_file = ENV_FILE


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

# Organization data
ORGANIZATIONS_EMAIL = "info@stereotipov.net"
ORGANIZATIONS_GROUP = "https://vk.com/socialrb02"
