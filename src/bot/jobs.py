import asyncio
from datetime import date
from urllib.parse import urljoin

from telegram import ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from src.bot.api_services import (
    get_member_service_callback,
    get_report_service_callback,
)
from src.core.db.db import get_session
from src.core.settings import settings


async def send_no_report_reminder_job(context: CallbackContext) -> None:
    """Отправить напоминание об отчёте."""
    session_generator = get_session()
    member_service = await get_member_service_callback(session_generator)
    current_day_of_month = date.today().day
    members = await member_service.get_members_with_no_reports(current_day_of_month)
    send_message_tasks = [
        await context.bot.send_message(
            chat_id=member.user.telegram_id,
            text=(
                f"f'{member.user.name} {member.user.surname}, мы потеряли тебя!"
                f"Задание все еще ждет тебя."
                f"Напоминаем, что за каждое выполненное задание ты получаешь виртуальные "
                f"\"ломбарьерчики\", которые можешь обменять на призы и подарки!"
            ),
        )
        for member in members
    ]
    context.application.create_task(asyncio.gather(*send_message_tasks))


async def send_daily_task_job(context: CallbackContext) -> None:
    buttons = ReplyKeyboardMarkup([["Пропустить задание", "Баланс ломбарьеров"]], resize_keyboard=True)
    session_generator = get_session()
    report_service = await get_report_service_callback(session_generator)
    member_service = await get_member_service_callback(session_generator)
    await member_service.exclude_lagging_members(context.application)
    current_day_of_month = date.today().day
    task, members = await report_service.get_today_task_and_active_members(current_day_of_month)
    task_photo = urljoin(settings.APPLICATION_URL, task.url)
    send_message_tasks = [
        context.bot.send_photo(
            chat_id=member.user.telegram_id,
            photo=task_photo,
            caption=(
                f"Привет, {member.user.name}!\n"
                f"Сегодня твоим заданием будет {task.description}. "
                f"Не забудь сделать фотографию, как ты выполняешь задание, и отправить на проверку."
            ),
            reply_markup=buttons,
        )
        for member in members
    ]
    context.application.create_task(asyncio.gather(*send_message_tasks))
