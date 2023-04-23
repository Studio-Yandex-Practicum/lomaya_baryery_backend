from datetime import time
from pathlib import Path

import pytz
from telegram.ext import (
    AIORateLimiter,
    Application,
    ApplicationBuilder,
    ChatMemberHandler,
    CommandHandler,
    MessageHandler,
    PicklePersistence,
    TypeHandler,
    filters,
)
from telegram.ext.filters import PHOTO, TEXT, Regex, StatusUpdate

from src.bot.handlers import (
    button_handler,
    chat_member_handler,
    get_web_app_query_data,
    incorrect_report_type_handler,
    photo_handler,
    start,
    web_app_data,
)
from src.bot.jobs import (
    finish_shift_automatically_job,
    send_daily_task_job,
    send_no_report_reminder_job,
)
from src.core.settings import settings

HANDLED_MESSAGE_TYPES = filters.PHOTO | filters.TEXT | filters.StatusUpdate.WEB_APP_DATA

RE_PATTERN: str = "Данные успешно отправлены боту"


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
    bot_instance.add_handler(
        TypeHandler(
            dict,
            get_web_app_query_data,
        )
    )
    bot_instance.add_handler(MessageHandler(Regex(RE_PATTERN), web_app_data))
    bot_instance.add_handler(ChatMemberHandler(chat_member_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    bot_instance.add_handler(CommandHandler("start", start))
    bot_instance.add_handler(MessageHandler(PHOTO, photo_handler))
    bot_instance.add_handler(MessageHandler(TEXT, button_handler))
    bot_instance.add_handler(MessageHandler(StatusUpdate.WEB_APP_DATA, web_app_data))
    bot_instance.add_handler(MessageHandler(~HANDLED_MESSAGE_TYPES, incorrect_report_type_handler))
    bot_instance.job_queue.run_daily(
        finish_shift_automatically_job,
        time(hour=settings.SEND_NEW_TASK_HOUR - 1, tzinfo=pytz.timezone(settings.TIME_ZONE)),
    )
    bot_instance.job_queue.run_daily(
        send_daily_task_job,
        time(hour=settings.SEND_NEW_TASK_HOUR, tzinfo=pytz.timezone(settings.TIME_ZONE)),
    )
    bot_instance.job_queue.run_daily(
        send_no_report_reminder_job,
        time(hour=settings.SEND_NO_REPORT_REMINDER_HOUR, tzinfo=pytz.timezone(settings.TIME_ZONE)),
    )
    return bot_instance


async def start_bot(webhook_mode: bool = settings.BOT_WEBHOOK_MODE) -> Application:
    """Запустить бота."""
    bot_instance = create_bot()
    await bot_instance.initialize()
    if webhook_mode:
        bot_instance.updater = None
        await bot_instance.bot.set_webhook(
            url=settings.telegram_webhook_url,
            secret_token=settings.SECRET_KEY,
        )
    else:
        await bot_instance.updater.start_polling()
    await bot_instance.start()
    return bot_instance
