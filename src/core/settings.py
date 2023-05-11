import os
import uuid
from datetime import time, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

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
    SEND_NO_REPORT_REMINDER_HOUR: int = 19  # время для напоминания о невыполненном задании
    MIN_AGE: int = 3  # минимальный возраст участника
    DAYS_FROM_START_OF_SHIFT_TO_JOIN: int = 2  # сколько дней от начала смены возможна регистрация
    MAX_REQUESTS: int = 3  # Максимальное число запросов на участие в смене
    HEALTHCHECK_API_URL: str
    DEBUG: bool = False
    SECRET_KEY: str = str(uuid.uuid4())
    MIN_PASSWORD_LENGTH: int = 8
    ROOT_PATH: str = "/api/"

    MAIL_SERVER: str = "smtp.yandex.ru"
    MAIL_PORT: int = 465
    MAIL_LOGIN: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    # количество заданий для исключения участника из смены, на которое подряд не было отправлено отчетов
    SEQUENTIAL_TASKS_PASSES_FOR_EXCLUDE: int = 5

    # Organization data
    ORGANIZATIONS_EMAIL: str = "lomayabaryery.noreply@yandex.ru"
    ORGANIZATIONS_GROUP: str = "https://vk.com/socialrb02"

    TIME_ZONE: str = "Asia/Yekaterinburg"

    # Logging settings
    LOG_LOCATION: str = "logs/warning.log"
    LOG_ROTATION: str = "12:00"
    LOG_COMPRESSION: str = "tar.gz"
    LOG_LEVEL: str = "WARNING"

    @property
    def database_url(self) -> str:
        """Получить ссылку для подключения к DB."""
        return (
            "postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def api_url(self) -> str:
        return urljoin(self.APPLICATION_URL, self.ROOT_PATH)

    @property
    def user_reports_dir(self) -> Path:
        """Получить директорию для сохранения фотоотчета."""
        return BASE_DIR / "static" / "user_reports"

    @property
    def user_reports_url(self) -> str:
        """Получить ссылку на изображения фотоотчетов."""
        return "/static/user_reports/"

    @property
    def registration_template_url(self) -> str:
        """Получить url-ссылку на HTML шаблон регистрации."""
        return urljoin(self.api_url, "telegram/registration_form")

    @property
    def telegram_webhook_url(self) -> str:
        """Получить url-ссылку на эндпоинт для работы telegram в режиме webhook."""
        return urljoin(self.api_url, "telegram/webhook")

    @property
    def registration_template(self) -> Path:
        """Получить HTML-шаблон формы регистрации."""
        return BASE_DIR / "src" / "templates" / "registration" / "registration.html"

    @property
    def task_image_url(self) -> str:
        """Получить ссылку на изображения заданий."""
        return "/static/tasks/"

    @property
    def task_image_dir(self) -> Path:
        """Получить директорию c изображениями заданий."""
        return BASE_DIR / "static" / "tasks"

    @property
    def email_template_directory(self) -> Path:
        """Получить директорию шаблонов электронной почты."""
        return BASE_DIR / "src" / "templates" / "email"

    @property
    def formatted_task_time(self) -> str:
        """Получить время отправки новых заданий."""
        dt = time(hour=8)
        return dt.strftime('%H')

    @property
    def swagger(self) -> Optional[str]:
        return None if self.DEBUG is False else "/docs"

    @property
    def redoc(self) -> Optional[str]:
        return None if self.DEBUG is False else "/redoc"

    class Config:
        env_file = ENV_FILE


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

NUMBER_ATTEMPTS_SUBMIT_REPORT: int = 3  # количество попыток для сдачи фотоотчета для одного задания
INVITE_LINK_EXPIRATION_TIME = timedelta(days=1)  # время существования ссылки для приглашения на регистрацию
