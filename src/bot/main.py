from datetime import time
from pathlib import Path
from urllib.parse import urljoin

import pytz
from telegram.ext import (
    AIORateLimiter,
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    PicklePersistence,
)
from telegram.ext.filters import PHOTO, StatusUpdate

from src.api.routers.telegram_webhook import TELEGRAM_WEBHOOK_ENDPOINT
from src.bot.handlers import photo_handler, start, web_app_data
from src.bot.jobs import (
    finish_shift_automatically_job,
    send_daily_task_job,
    send_no_report_reminder_job,
    start_shift_automatically_job,
)
from src.core.settings import settings


def create_bot() -> Application:
    """Создать бота."""
    Path(settings.user_reports_dir).mkdir(parents=True, exist_ok=True)
    bot_persistence = PicklePersistence(filepath=settings.BOT_PERSISTENCE_FILE)
    bot_instance = (
        ApplicationBuilder()
        .token(settings.BOT_TOKEN)
        .rate_limiter(AIORateLimiter())
        .persistence(persistence=bot_persistence)
        .build()
    )
    bot_instance.add_handler(CommandHandler("start", start))
    bot_instance.add_handler(MessageHandler(PHOTO, photo_handler))
    bot_instance.add_handler(MessageHandler(StatusUpdate.WEB_APP_DATA, web_app_data))
    bot_instance.job_queue.run_daily(
        finish_shift_automatically_job,
        time(hour=settings.SEND_NEW_TASK_HOUR - 1, tzinfo=pytz.timezone("Europe/Moscow")),
    )
    bot_instance.job_queue.run_daily(
        start_shift_automatically_job,
        time(hour=settings.SEND_NEW_TASK_HOUR, tzinfo=pytz.timezone("Europe/Moscow")),
    )
    bot_instance.job_queue.run_daily(
        send_daily_task_job,
        time(
            hour=settings.SEND_NEW_TASK_HOUR,
            minute=5,  # Оставляем задержку для гарантированного старта смены
            tzinfo=pytz.timezone("Europe/Moscow"),
        ),
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
