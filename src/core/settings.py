import os
from pathlib import Path
from urllib.parse import urlparse

import aiohttp
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
    NGROK_LOCAL_URL: str

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
        user_reports_dir = BASE_DIR / 'data' / 'user_reports'
        Path(user_reports_dir).mkdir(parents=True, exist_ok=True)
        return user_reports_dir

    @property
    async def registration_template_url(self) -> str:
        """URL для шаблона регистрации."""
        prefix = "registration_template"
        if self.BOT_WEBHOOK_MODE:
            url = urlparse(f"{self.APPLICATION_URL}/{prefix}", "https")
        # Для теста получаем url на котором работает ngrok
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(settings.NGROK_LOCAL_URL) as response:
                    res_json = await response.json()
                    url = urlparse(f"{res_json['tunnels'][0]['public_url']}/{prefix}", "https")
        return url.geturl()

    class Config:
        env_file = ENV_FILE


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

# Organization data
ORGANIZATIONS_EMAIL = "info@stereotipov.net"
ORGANIZATIONS_GROUP = "https://vk.com/socialrb02"
