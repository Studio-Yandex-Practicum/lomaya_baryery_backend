from urllib.parse import urljoin

from telegram.ext import Application, ApplicationBuilder, CommandHandler

from src.api.routers import TELEGRAM_WEBHOOK_ENDPOINT
from src.bot.handlers import start
from src.core.settings import settings


def create_bot() -> Application:
    """Создать бота."""
    bot_instance = ApplicationBuilder().token(settings.BOT_TOKEN).build()
    bot_instance.add_handler(CommandHandler("start", start))
    return bot_instance


async def initialize_bot_on_polling_mode(bot_instance: Application) -> None:
    """Инициализировать бота в режиме polling."""
    await bot_instance.initialize()
    await bot_instance.updater.start_polling()


async def initialize_bot_on_webhook_mode(bot_instance: Application) -> None:
    """Инициализировать бота в режиме webhook."""
    bot_instance.updater = None
    await bot_instance.bot.set_webhook(
        url=urljoin(settings.APPLICATION_URL, TELEGRAM_WEBHOOK_ENDPOINT),
        secret_token=settings.BOT_TOKEN.replace(':', '')  # colon is not allowed here
    )
    await bot_instance.initialize()


async def start_bot(webhook_mode: bool = settings.BOT_WEBHOOK_MODE) -> Application:
    """Запустить бота."""
    bot_instance = create_bot()
    if webhook_mode:
        await initialize_bot_on_webhook_mode(bot_instance)
    else:
        await initialize_bot_on_polling_mode(bot_instance)
    await bot_instance.start()
    return bot_instance
