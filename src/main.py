from urllib.parse import urljoin

from fastapi import FastAPI
from telegram.ext import ApplicationBuilder, CommandHandler, Application

from src.api.routers import router, webhook_router, TELEGRAM_WEBHOOK_ENDPOINT
from src.bot.handlers import start
from src.core.settings import settings

app = FastAPI()

app.include_router(router)

if settings.BOT_WEBHOOK_MODE:
    app.include_router(webhook_router)


def create_bot() -> Application:
    """Создать бота."""
    bot_app = ApplicationBuilder().token(settings.BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    return bot_app


async def bot_init_polling_mode(bot_app: Application) -> None:
    """Инициализировать бота в режиме polling."""
    await bot_app.initialize()
    await bot_app.updater.start_polling()


async def bot_init_webhook_mode(bot_app: Application) -> None:
    """Инициализировать бота в режиме webhook"""
    bot_app.updater = None
    await bot_app.bot.set_webhook(
        url=urljoin(settings.APPLICATION_URL, TELEGRAM_WEBHOOK_ENDPOINT),
        secret_token=settings.BOT_TOKEN.replace(':', '')  # colon is not allowed here # noqa
    )
    await bot_app.initialize()


async def start_bot(
    webhook_mode: bool = settings.BOT_WEBHOOK_MODE
) -> Application:
    """Запустить бота."""
    bot_app = create_bot()
    if webhook_mode:
        await bot_init_webhook_mode(bot_app)
    else:
        await bot_init_polling_mode(bot_app)
    await bot_app.start()
    # storing bot_app to extra state of FastAPI app instance
    # refer to https://www.starlette.io/applications/#storing-state-on-the-app-instance
    app.state.bot_app = bot_app
    return bot_app
