from datetime import time
from urllib.parse import urljoin

import pytz
from telegram.ext import Application, ApplicationBuilder, CommandHandler

from src.api.routers.hello import TELEGRAM_WEBHOOK_ENDPOINT
from src.bot.handlers import start
from src.bot.jobs import send_daily_task_job, send_no_report_reminder_job
from src.core.settings import settings


def create_bot() -> Application:
    """Создать бота."""
    bot_instance = ApplicationBuilder().token(settings.BOT_TOKEN).build()
    bot_instance.add_handler(CommandHandler("start", start))
    bot_instance.job_queue.run_daily(
        send_daily_task_job, time(hour=settings.SEND_NEW_TASK_HOUR, tzinfo=pytz.timezone("Europe/Moscow"))
    )
    bot_instance.job_queue.run_daily(
        send_no_report_reminder_job,
        time(hour=settings.SEND_NO_REPORT_REMINDER_HOUR, tzinfo=pytz.timezone("Europe/Moscow")),
    )
    return bot_instance


async def start_bot(webhook_mode: bool = settings.BOT_WEBHOOK_MODE) -> Application:
    """Запустить бота."""
    bot_instance = create_bot()
    await bot_instance.initialize()
    if webhook_mode:
        bot_instance.updater = None
        await bot_instance.bot.set_webhook(
            url=urljoin(settings.APPLICATION_URL, TELEGRAM_WEBHOOK_ENDPOINT),
            secret_token=settings.BOT_TOKEN.replace(':', ''),  # colon is not allowed here
        )
    else:
        await bot_instance.updater.start_polling()
    await bot_instance.start()
    return bot_instance
