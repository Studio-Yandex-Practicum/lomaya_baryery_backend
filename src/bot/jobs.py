from datetime import datetime, time
import pytz

from telegram.ext import CallbackContext

from src.core.db import models
from src.main import create_bot


bot = create_bot().bot  # временная копия бота до миграции на webhooks


async def start_reminder(context: CallbackContext) -> None:
    """Добавить в очередь и выполнить отправку напоминания в 20:00."""
    dt = datetime(
        year=datetime.now().year,
        month=datetime.now().month,
        day=datetime.now().day,
        hour=20
    )
    tm = pytz.timezone("Europe/Moscow").localize(dt).timetz()
    context.job_queue.run_once(send_reminder_job, tm)


async def send_reminder_job(user: models.User) -> None:
    """Отправить напоминание."""
    await bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"{user.name} {user.surname}, мы потеряли тебя! Напоминаем, "
            f"что за каждое выполненное задание ты получаешь виртуальные "
            f"«ломбарьерчики», которые можешь обменять на призы и подарки!"
        )
    )


async def start_task(context: CallbackContext) -> None:
    """Добавить в очередь и выполнить метод отправки задания в 8:00."""
    tm = time(hour=8, tzinfo=pytz.timezone("Europe/Moscow"))
    context.job_queue.run_daily(send_method_job, tm)


async def send_method_job():
    """Метод отправки задания."""
    ...
