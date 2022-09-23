from fastapi import FastAPI
from telegram.ext import ApplicationBuilder, CommandHandler

from src.api.main_router import main_router
from src.bot.handlers import start
from src.core.settings import settings

app = FastAPI()

app.include_router(main_router)


def create_bot():
    """Создать бота."""
    bot_app = ApplicationBuilder().token(settings.BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    return bot_app


async def start_bot():
    """Запустить бота."""
    bot_app = create_bot()
    await bot_app.updater.initialize()
    await bot_app.initialize()
    await bot_app.updater.start_polling()
    await bot_app.start()
