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
from src.bot.services import BotService
from src.core.db.db import get_session
from src.core.db.models import Report, Shift
from src.core.settings import settings

LOMBARIERS_BALANCE = 'Баланс ломбарьеров'
SKIP_A_TASK = 'Пропустить задание'


async def send_no_report_reminder_job(context: CallbackContext) -> None:
    """Отправить напоминание об отчёте."""
    member_session_generator = get_session()
    member_service = await get_member_service_callback(member_session_generator)
    bot_service = BotService(context)
    members = await member_service.get_members_with_no_reports()
    send_message_tasks = [
        bot_service.send_message(
            member.user,
            (
                f"{member.user.name} {member.user.surname}, мы потеряли тебя!"
                f"Задание все еще ждет тебя."
                f"Напоминаем, что за каждое выполненное задание ты получаешь виртуальные "
                f"\"ломбарьерчики\", которые можешь обменять на призы и подарки!"
            ),
        )
        for member in members
    ]
    context.application.create_task(asyncio.gather(*send_message_tasks))


async def send_daily_task_job(context: CallbackContext) -> None:
    buttons = ReplyKeyboardMarkup([[SKIP_A_TASK, LOMBARIERS_BALANCE]], resize_keyboard=True)
    report_session_generator = get_session()
    member_session_generator = get_session()
    report_service = await get_report_service_callback(report_session_generator)
    member_service = await get_member_service_callback(member_session_generator)
    bot_service = BotService(context)
    await member_service.exclude_lagging_members(context.application)
    current_day_of_month = date.today().day
    reports_list = await report_service.get_waiting_reports()
    await report_service.set_status_to_reports(reports_list, Report.Status.SKIPPED)
    task, members = await report_service.get_today_task_and_active_members(current_day_of_month)
    await report_service.create_daily_reports(members, task)
    task_photo = urljoin(settings.APPLICATION_URL, task.url)
    send_message_tasks = [
        bot_service.send_photo(
            member.user,
            task_photo,
            (
                f"Привет, {member.user.name}!\n"
                f"Сегодня твоим заданием будет {task.description_for_message}. "
                f"Не забудь сделать фотографию, как ты выполняешь задание, и отправить на проверку."
            ),
            buttons,
        )
        for member in members
    ]
    context.application.create_task(asyncio.gather(*send_message_tasks))


async def finish_shift_automatically_job(context: CallbackContext) -> None:
    """Автоматически закрывает смену в дату, указанную в finished_at."""
    session = get_session()
    shift_service = await get_shift_service_callback(session)
    await shift_service.finish_shift_automatically(context.application)


async def start_shift_automatically_job(context: CallbackContext) -> None:
    """Автоматически запускает смену в дату, указанную в started_at."""
    session = get_session()
    shift_service = await get_shift_service_callback(session)
    shifts = await shift_service.list_all_shifts(status=[Shift.Status.PREPARING])
    if shifts:
        shift = shifts[0]
        if shift.started_at == date.today():
            await shift_service.start_shift(_id=shift.id)
