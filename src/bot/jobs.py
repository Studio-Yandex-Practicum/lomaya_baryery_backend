import asyncio
from datetime import date
from urllib.parse import urljoin

from telegram import ReplyKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import CallbackContext

from src.bot.api_services import (
    get_member_service_callback,
    get_report_service_callback,
    get_user_service_callback,
)
from src.core.db.db import get_session
from src.core.db.models import Member
from src.core.settings import settings


async def send_message(member: Member, context: CallbackContext):
    try:
        await context.bot.send_message(
            chat_id=member.user.telegram_id,
            text=(
                f"f'{member.user.name} {member.user.surname}, мы потеряли тебя!"
                f"Задание все еще ждет тебя."
                f"Напоминаем, что за каждое выполненное задание ты получаешь виртуальные "
                f"\"ломбарьерчики\", которые можешь обменять на призы и подарки!"
            ),
        )
    except TelegramError:
        session = get_session()
        user_service = await get_user_service_callback(session)
        await user_service.telegram_blocked_change(member.user, True)


async def send_no_report_reminder_job(context: CallbackContext) -> None:
    """Отправить напоминание об отчёте."""
    session_generator = get_session()
    member_service = await get_member_service_callback(session_generator)
    members = await member_service.get_members_with_no_reports()
    send_message_tasks = [send_message(member, context) for member in members]
    context.application.create_task(asyncio.gather(*send_message_tasks))


async def send_photo(member: Member, context: CallbackContext, task, task_photo, buttons):
    try:
        await context.bot.send_photo(
            chat_id=member.user.telegram_id,
            photo=task_photo,
            caption=(
                f"Привет, {member.user.name}!\n"
                f"Сегодня твоим заданием будет {task.description}. "
                f"Не забудь сделать фотографию, как ты выполняешь задание, и отправить на проверку."
            ),
            reply_markup=buttons,
        )
    except TelegramError:
        session = get_session()
        user_service = await get_user_service_callback(session)
        await user_service.telegram_blocked_change(member.user, True)


async def send_daily_task_job(context: CallbackContext) -> None:
    buttons = ReplyKeyboardMarkup([["Пропустить задание", "Баланс ломбарьеров"]], resize_keyboard=True)
    report_session_generator = get_session()
    member_session_generator = get_session()
    report_service = await get_report_service_callback(report_session_generator)
    member_service = await get_member_service_callback(member_session_generator)
    await member_service.exclude_lagging_members(context.application)
    current_day_of_month = date.today().day
    task, members = await report_service.get_today_task_and_active_members(current_day_of_month)
    await report_service.create_daily_reports(members, task)
    task_photo = urljoin(settings.APPLICATION_URL, task.url)
    send_message_tasks = [send_photo(member, context, task, task_photo, buttons) for member in members]
    context.application.create_task(asyncio.gather(*send_message_tasks))
