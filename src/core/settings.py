import os
from datetime import timedelta
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
    SEND_NEW_TASK_HOUR: int = 8  # время для отправки задания
    SEND_NO_REPORT_REMINDER_HOUR: int = 20  # время для напоминания о невыполненном задании
    MIN_AGE: int = 3  # минимальный возраст участника
    DAYS_FROM_START_OF_SHIFT_TO_JOIN: int = 2  # сколько дней от начала смены возможна регистрация
    MAX_REQUESTS: int = 3  # Максимальное число запросов на участие в смене
    HEALTHCHECK_API_URL: str
    DEBUG: bool = False

    MAIL_SERVER: str = "smtp.ethereal.email"
    MAIL_PORT: int = 587
    MAIL_LOGIN: str = "michel.bruen24@ethereal.email"
    MAIL_PASSWORD: str = "tM7wbvvvtmRrWy54PD"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    # количество заданий для исключения участника из смены, на которое подряд не было отправлено отчетов
    SEQUENTIAL_TASKS_PASSES_FOR_EXCLUDE: int = 5

    @property
    def database_url(self):
        """Получить ссылку для подключения к DB."""
        return (
            "postgresql+asyncpg://"
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

    @property
    def email_template_directory(self):
        """Получить директорию шаблонов электронной почты."""
        return BASE_DIR / "src/templates/email"

    class Config:
        env_file = ENV_FILE


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

# Organization data
ORGANIZATIONS_EMAIL = "info@stereotipov.net"
ORGANIZATIONS_GROUP = "https://vk.com/socialrb02"
NUMBER_ATTEMPTS_SUMBIT_REPORT: int = 3  # количество попыток для сдачи фотоотчета для одного задания
INVITE_LINK_EXPIRATION_TIME = timedelta(days=1)  # время существования ссылки для приглашения на регистрацию
