from urllib.parse import urljoin

from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, Application

from src.api.routers import router
from src.bot.handlers import start
from src.core.settings import BOT_TOKEN, BOT_WEBHOOK_MODE, BOT_WEBHOOK_URL

app = FastAPI()

app.include_router(router)

BOT_WEBHOOK_ENDPOINT = '/telegram_webhook'
BOT_WEBHOOK_FULL_URL = urljoin(BOT_WEBHOOK_URL, BOT_WEBHOOK_ENDPOINT)


def create_bot() -> Application:
    """Создать бота."""
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
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
    await bot_app.bot.set_webhook(url=BOT_WEBHOOK_FULL_URL)
    await bot_app.initialize()
    app.state.bot_app = bot_app


async def start_bot() -> None:
    """Запустить бота."""
    bot_app = create_bot()
    if BOT_WEBHOOK_MODE:
        await bot_init_webhook_mode(bot_app)
    else:
        await bot_init_polling_mode(bot_app)
    await bot_app.start()


@app.post(BOT_WEBHOOK_ENDPOINT)
async def get_telegram_bot_updates(request: Request):
    """Получение обновлений telegram в режиме работы бота webhook."""
    bot_app = request.app.state.bot_app
    request_json_data = await request.json()
    await bot_app.update_queue.put(
        Update.de_json(data=request_json_data, bot=bot_app.bot)
    )
    return request_json_data
