from datetime import date
from urllib.parse import urljoin

from telegram import ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from src.bot.api_services import get_report_service_callback
from src.core.db.db import get_session
from src.core.settings import settings


async def send_no_report_reminder_job(context: CallbackContext) -> None:
    """Отправить напоминание об отчёте."""
    await context.bot.send_message(
        chat_id='5702444617',  # заменить на user.telegram_id
        text=(
            f"<user.name> <user.surname>, мы потеряли тебя! Напоминаем, "  # noqa добавить user.name и user.surname
            f"что за каждое выполненное задание ты получаешь виртуальные "
            f"\"ломбарьерчики\", которые можешь обменять на призы и подарки!"
        ),
    )


async def send_daily_task_job(context: CallbackContext) -> None:
    buttons = ReplyKeyboardMarkup([["Пропустить задание", "Баланс ломбарьеров"]], resize_keyboard=True)
    session_generator = get_session()
    report_service = await get_report_service_callback(session_generator)
    await report_service.exclude_members_from_shift(context.bot)
    current_day_of_month = date.today().day
    task, members = await report_service.get_today_task_and_active_members(current_day_of_month)
    for member in members:
        await context.bot.send_photo(
            chat_id=member.user.telegram_id,
            photo=urljoin(settings.APPLICATION_URL, task.url),
            caption=(
                f"Привет, {member.user.name}!\n"
                f"Сегодня твоим заданием будет {task.description}. "
                f"Не забудь сделать фотографию, как ты выполняешь задание, и отправить на проверку."
            ),
            reply_markup=buttons,
        )
