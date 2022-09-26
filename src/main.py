from fastapi import FastAPI
from telegram.ext import ApplicationBuilder, CommandHandler

from src.api.routers import router
from src.bot.handlers import start
from src.bot.jobs import (
    get_sending_reminder_time_callback,
    get_sending_task_time_callback,
    send_new_task_job,
    send_no_report_reminder_job,
)
from src.core.settings import settings

app = FastAPI()

app.include_router(router)


def create_bot():
    """Создать бота."""
    bot_app = ApplicationBuilder().token(settings.BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.job_queue.run_daily(
        send_new_task_job,
        get_sending_task_time_callback()
    )
    bot_app.job_queue.run_once(
        send_no_report_reminder_job,
        get_sending_reminder_time_callback()
    )
    return bot_app


async def start_bot():
    """Запустить бота."""
    bot_app = create_bot()
    await bot_app.updater.initialize()
    await bot_app.initialize()
    await bot_app.updater.start_polling()
    await bot_app.start()
