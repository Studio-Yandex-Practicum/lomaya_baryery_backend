import os
import uuid
from datetime import time, timedelta
from functools import cache
from pathlib import Path
from urllib.parse import urljoin

from pydantic import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if os.path.exists(str(BASE_DIR / ".env")):
    ENV_FILE = ".env"
else:
    ENV_FILE = ".env.example"


class Settings(BaseSettings):
    """Настройки проекта."""

    DEBUG: bool = False

    # Настройки telegram-бота
    BOT_TOKEN: str  # Токен аутентификации бота
    BOT_WEBHOOK_MODE: bool = False  # запустить бота в режиме webhook(true)|polling(false)
    BOT_PERSISTENCE_FILE: str = str(BASE_DIR / "src" / "bot" / "bot_persistence_file")

    # Настройки взаимодействия с БД
    POSTGRES_DB: str  # Имя базы данных
    POSTGRES_USER: str  # имя пользователя ля для подключения к БД
    POSTGRES_PASSWORD: str  # пароль для подключения к БД
    DB_HOST: str  # название сервиса (контейнера)
    DB_PORT: str  # порт для подключения к БД

    # Схема и домен, на котором развернуто приложение (например: http://example.net)
    APPLICATION_URL: str

    # При работе за reverse proxy, дополнительный путь, который добавляется этим прокси.
    ROOT_PATH: str = "/api/"

    # секретный ключ для генерации jwt-токенов
    SECRET_KEY: str = str(uuid.uuid4())

    # Эндпоинт для проверки API
    HEALTHCHECK_API_URL: str

    # Временная зона, в которой мы работаем,
    # в формате IANA Time Zone Database (aka zoneinfo, aka tzdata, aka Olson database)
    TIME_ZONE: str = "Asia/Yekaterinburg"

    # Organization data
    ORGANIZATIONS_EMAIL: str = "lomayabaryery.noreply@yandex.ru"
    ORGANIZATIONS_GROUP: str = "https://vk.com/socialrb02"  # используется при отправке сообщений пользователям

    # Количество заданий для исключения участника из смены.
    # Участник исключается из смены, если он пропустил или не отправил указанное количество отчётов подряд
    SEQUENTIAL_TASKS_PASSES_FOR_EXCLUDE: int = 5

    # Минимальная длина пароля администратора
    MIN_PASSWORD_LENGTH: int = 8

    # Время (час) для отправки нового задания
    SEND_NEW_TASK_HOUR: int = 8

    # Время (час) для напоминания о невыполненном задании
    SEND_NO_REPORT_REMINDER_HOUR: int = 19

    # Минимальный возраст участника
    MIN_AGE: int = 3

    # Сколько дней от начала смены возможна регистрация
    DAYS_FROM_START_OF_SHIFT_TO_JOIN: int = 2

    # Максимальное число запросов на участие в смене
    MAX_REQUESTS: int = 3

    # Количество попыток для сдачи фотоотчета для одного задания
    NUMBER_ATTEMPTS_SUBMIT_REPORT: int = 3

    # Время жизни ссылки для приглашения на регистрацию
    INVITE_LINK_EXPIRATION_TIME = timedelta(days=1)

    # Директория для сохранения фотоотчётов
    USER_REPORTS_DIR: Path = BASE_DIR / "static" / "user_reports"

    # Базовый путь к изображениям фотоотчётов
    USER_REPORTS_URL: str = "/static/user_reports/"

    # Базовый путь к изображениям заданий
    TASK_IMAGE_URL: str = "/static/tasks/"

    # Директория с изображениями заданий
    TASK_IMAGE_DIR: Path = BASE_DIR / "static" / "tasks"

    # Путь до HTML-шаблона формы регистрации
    REGISTRATION_TEMPLATE: Path = BASE_DIR / "src" / "templates" / "registration" / "registration.html"

    # Директория с шаблонами электронной почты
    EMAIL_TEMPLATE_DIRECTORY: Path = BASE_DIR / "src" / "templates" / "email"

    # Отформатированное время отправки нового задания. Используется при формировании сообщений пользователям
    FORMATTED_TASK_TIME: str = time(hour=8).strftime("%H")

    # Настройки отправки сообщений через электронную почту
    MAIL_SERVER: str = "smtp.yandex.ru"  # адрес почтового сервиса
    MAIL_PORT: int = 465  # порт для подключения к почтовому сервису
    MAIL_LOGIN: str = ""  # логин для подключения к почтовому сервису
    MAIL_PASSWORD: str = ""  # пароль для подключения к почтовому сервису
    MAIL_STARTTLS: bool = False  # использовать STARTTLS или нет
    MAIL_SSL_TLS: bool = True  # использовать SSL/TLS или нет
    USE_CREDENTIALS: bool = True  # использовать логин/пароль для подключения к почтовому серверу или нет
    VALIDATE_CERTS: bool = True  # проверять SSL сертификат почтового сервера или нет

    # Logging settings
    LOG_LOCATION: str = "logs/warning.log"
    LOG_ERROR_LOCATION: str = "logs/error.log"
    LOG_ROTATION_TIME: str = "12:00"
    LOG_COMPRESSION: str = "tar.gz"
    LOG_LEVEL: str = "WARNING"
    LOG_ERROR_LEVEL: str = "ERROR"

    # Относительный путь к Swagger UI
    @property
    def swagger(self):
        return "/docs" if self.DEBUG else None

    # Относительный путь к ReDoc UI
    @property
    def redoc(self):
        return "/redoc" if self.DEBUG else None

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
        """Получить URL-ссылку на API."""
        return urljoin(self.APPLICATION_URL, self.ROOT_PATH)

    @property
    def registration_template_url(self) -> str:
        """Получить url-ссылку на HTML шаблон регистрации."""
        return urljoin(self.api_url, "telegram/registration_form")

    @property
    def telegram_webhook_url(self) -> str:
        """Получить url-ссылку на эндпоинт для работы telegram в режиме webhook."""
        return urljoin(self.api_url, "telegram/webhook")

    class Config:
        env_file = ENV_FILE


@cache
def get_settings():
    return Settings()


settings = get_settings()
