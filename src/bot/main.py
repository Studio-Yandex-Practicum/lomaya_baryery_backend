from urllib.parse import urljoin

from telegram.ext import ApplicationBuilder, CommandHandler, Application

from src.api.routers import TELEGRAM_WEBHOOK_ENDPOINT
from src.bot.handlers import start
from src.core.settings import settings


def create_bot() -> Application:
    """Создать бота."""
    bot_app = ApplicationBuilder().token(settings.BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    return bot_app


async def set_bot_to_polling(bot_app: Application) -> None:
    """Инициализировать бота в режиме polling."""
    await bot_app.initialize()
    await bot_app.updater.start_polling()


async def set_bot_to_webhook(bot_app: Application) -> None:
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
        await set_bot_to_webhook(bot_app)
    else:
        await set_bot_to_polling(bot_app)
    await bot_app.start()
    return bot_app
