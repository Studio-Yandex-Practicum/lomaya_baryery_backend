from datetime import datetime, time

import pytz
from telegram.ext import CallbackContext

from src.core.db import models
from src.core.settings import settings


def get_sending_reminder_time_callback():
    """Получить время отправки напоминания об отчёте."""
    dt = datetime(
        year=datetime.now().year,
        month=datetime.now().month,
        day=datetime.now().day,
        hour=settings.SEND_NO_REPORT_REMINDER_HOUR
    )
    return pytz.timezone("Europe/Moscow").localize(dt).timetz()


async def send_no_report_reminder_job(
    context: CallbackContext, user: models.User
) -> None:
    """Отправить напоминание об отчёте."""
    await context.bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"{user.name} {user.surname}, мы потеряли тебя! Напоминаем, "
            f"что за каждое выполненное задание ты получаешь виртуальные "
            f"«ломбарьерчики», которые можешь обменять на призы и подарки!"
        )
    )


def get_sending_task_time_callback():
    """Получить время отправки нового задания."""
    return time(
        hour=settings.SEND_NEW_TASK_HOUR,
        tzinfo=pytz.timezone("Europe/Moscow")
    )


async def send_new_task_job(context: CallbackContext)  -> None:
    """Метод отправки нового задания."""
    ...
