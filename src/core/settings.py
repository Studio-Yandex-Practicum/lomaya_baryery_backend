from pathlib import Path

from environs import Env

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = Env()
env.read_env(str(BASE_DIR / ".env"))

# BOT settings
BOT_TOKEN = env("BOT_TOKEN")

# DB settings
DB_NAME = env("DB_NAME")  # имя базы данных
POSTGRES_USER = env("POSTGRES_USER")  # логин для подключения к базе данных
POSTGRES_PASSWORD = env("POSTGRES_PASSWORD")  # пароль для подключения к БД (установите свой) # noqa
DB_HOST = env("DB_HOST")  # название сервиса (контейнера)
DB_PORT = env("DB_PORT")  # порт для подключения к БД

DATABASE_URL = (
    "postgresql+asyncpg://"
    f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
