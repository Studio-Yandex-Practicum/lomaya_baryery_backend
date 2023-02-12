import asyncio
from datetime import date
from urllib.parse import urljoin

from telegram import ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from src.bot.api_services import (
    get_member_service_callback,
    get_report_service_callback,
    get_shift_service_callback,
)
from src.bot.handlers import error_handler
from src.core.db.db import get_session
from src.core.db.models import Member, Shift
from src.core.settings import settings


async def send_no_report_reminder_job(context: CallbackContext) -> None:
    """Отправить напоминание об отчёте."""
    session_generator = get_session()
    member_service = await get_member_service_callback(session_generator)
    members = await member_service.get_members_with_no_reports()

    async def send_message(member: Member):
        try:
            await context.bot.send_message(
                chat_id=member.user.telegram_id,
                text=(
                    f"{member.user.name} {member.user.surname}, мы потеряли тебя!"
                    f"Задание все еще ждет тебя."
                    f"Напоминаем, что за каждое выполненное задание ты получаешь виртуальные "
                    f"\"ломбарьерчики\", которые можешь обменять на призы и подарки!"
                ),
            )
        except Exception as e:
            context._chat_id, context.error = member.user.telegram_id, e
            await error_handler(update=None, context=context)

    send_message_tasks = [send_message(member) for member in members if not member.user.telegram_blocked]
    context.application.create_task(asyncio.gather(*send_message_tasks))


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

    async def send_photo(member: Member):
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
        except Exception as e:
            context._chat_id, context.error = member.user.telegram_id, e
            await error_handler(update=None, context=context)

    send_message_tasks = [send_photo(member) for member in members if not member.user.telegram_blocked]
    context.application.create_task(asyncio.gather(*send_message_tasks))


async def start_shift_automatically_job(context: CallbackContext) -> None:
    """Автоматически запускает смену в дату, указанную в started_at."""
    session = get_session()
    shift_service = await get_shift_service_callback(session)
    shifts = await shift_service.list_all_shifts(status=Shift.Status.PREPARING)
    if shifts:
        shift = shifts[0]
        if shift.started_at == date.today():
            await shift_service.start_shift(id=shift.id)
