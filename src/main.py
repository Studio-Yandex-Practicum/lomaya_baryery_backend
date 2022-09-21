from urllib.parse import urljoin

from fastapi import FastAPI
from telegram.ext import ApplicationBuilder, CommandHandler, Application

from src.api.routers import router
from src.bot.handlers import start
from src.core.settings import settings

app = FastAPI()

app.include_router(router)


def create_bot() -> Application:
    """Создать бота."""
    bot_app = ApplicationBuilder().token(settings.BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    return bot_app


async def bot_init_polling_mode(bot_app: Application) -> None:
    """Инициализировать бота в режиме polling."""
    await bot_app.updater.initialize()
    await bot_app.initialize()
    await bot_app.updater.start_polling()


async def bot_init_webhook_mode(bot_app: Application) -> None:
    """Инициализировать бота в режиме webhook"""
    bot_app.updater = None
    await bot_app.bot.set_webhook(
        url=urljoin(settings.APPLICATION_URL, 'telegram_handler'),
        secret_token=settings.BOT_TOKEN
    )
    await bot_app.initialize()
    app.state.bot_app = bot_app


async def start_bot() -> None:
    """Запустить бота."""
    bot_app = create_bot()
    if settings.BOT_WEBHOOK_MODE:
        await bot_init_webhook_mode(bot_app)
    else:
        await bot_init_polling_mode(bot_app)
    await bot_app.start()
