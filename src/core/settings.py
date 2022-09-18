from pathlib import Path

from environs import Env

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = Env()
env.read_env(str(BASE_DIR / ".env"))

# BOT settings
BOT_TOKEN = env("BOT_TOKEN")
BOT_WEBHOOK_MODE = env("BOT_WEBHOOK_MODE", "False").lower() in ('true', '1')  # запустить бота в режиме webhook(true)|polling(false) # noqa
BOT_WEBHOOK_URL = env("BOT_WEBHOOK_URL")  # URL для получения апдейтов в режиме webhook # noqa

# DB settings
DB_NAME = env("POSTGRES_DB")  # имя базы данных
POSTGRES_USER = env("POSTGRES_USER")  # логин для подключения к базе данных
POSTGRES_PASSWORD = env("POSTGRES_PASSWORD")  # пароль для подключения к БД (установите свой) # noqa
DB_HOST = env("DB_HOST")  # название сервиса (контейнера)
DB_PORT = env("DB_PORT")  # порт для подключения к БД

DATABASE_URL = (
    "postgresql+asyncpg://"
    f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
