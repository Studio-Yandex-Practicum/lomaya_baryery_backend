from urllib.parse import urljoin, quote

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


async def start_bot() -> None:
    """Запустить бота."""
    bot_app = create_bot()
    await bot_app.updater.initialize()
    await bot_app.initialize()
    if settings.BOT_WEBHOOK_MODE:
        webhook_settings = get_bot_webhook_settings()
        await bot_app.updater.start_webhook(**webhook_settings)
    else:
        await bot_app.updater.start_polling()
    await bot_app.start()


def get_bot_webhook_settings() -> dict:
    """Сгенерировать настройки для запуска бота в режиме webhook."""
    url_path = quote(settings.BOT_TOKEN)
    webhook_url = urljoin(settings.BOT_WEBHOOK_URL, url_path)
    return {
        'listen': '0.0.0.0',
        'port': settings.BOT_WEBHOOK_PORT,
        'url_path': url_path,
        'webhook_url': webhook_url
    }
