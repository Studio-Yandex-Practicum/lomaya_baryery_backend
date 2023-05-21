import asyncio
from datetime import date
from urllib.parse import urljoin

from telegram.ext import CallbackContext

from src.bot.api_services import (
    get_member_service_callback,
    get_report_service_callback,
    get_shift_service_callback,
)
from src.bot.services import BotService
from src.bot.ui import DAILY_TASK_BUTTONS
from src.core.db.db import get_session
from src.core.db.models import Report
from src.core.settings import settings


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
                f"{member.user.name} {member.user.surname}, мы потеряли тебя! "
                f"Задание все еще ждет тебя. "
                f"Напоминаем, что за каждое выполненное задание ты получаешь виртуальные "
                f"\"ломбарьерчики\", которые можешь обменять на призы и подарки!"
            ),
        )
        for member in members
    ]
    context.application.create_task(asyncio.gather(*send_message_tasks))


async def send_daily_task_job(context: CallbackContext) -> None:
    """Автоматически запускает смену и рассылает задания."""
    shift_session = get_session()
    shift_service = await get_shift_service_callback(shift_session)
    started_shift = await shift_service.get_started_shift_or_none()
    await shift_service.start_prepared_shift()
    if not started_shift:
        return
    member_session = get_session()
    member_service = await get_member_service_callback(member_session)
    report_session = get_session()
    report_service = await get_report_service_callback(report_session)
    bot_service = BotService(context)

    await report_service.set_status_to_waiting_reports(Report.Status.SKIPPED)
    await member_service.exclude_lagging_members(started_shift, context.application)
    task, members = await report_service.get_today_task_and_active_members(started_shift, date.today().day)
    await report_service.create_daily_reports(members, task)
    task_photo = urljoin(settings.APPLICATION_URL, task.url)
    send_message_tasks = [
        bot_service.send_photo(
            member.user,
            task_photo,
            (
                f"Привет, {member.user.name}!\n"
                f"Вчерашнее задание не было выполнено! Сегодня можешь отправить отчет только по новому заданию. "
                f"Сегодня твоим заданием будет {task.title}. "
                f"Не забудь сделать фотографию, как ты выполняешь задание, и отправить на проверку."
            )
            if await report_service.is_previous_report_not_submitted(member.id)
            else (
                f"Привет, {member.user.name}!\n"
                f"Сегодня твоим заданием будет {task.title}. "
                f"Не забудь сделать фотографию, как ты выполняешь задание, и отправить на проверку."
            ),
            DAILY_TASK_BUTTONS,
        )
        for member in members
    ]
    context.application.create_task(asyncio.gather(*send_message_tasks))


async def finish_shift_automatically_job(context: CallbackContext) -> None:
    """Автоматически закрывает смену в дату, указанную в finished_at."""
    session = get_session()
    shift_service = await get_shift_service_callback(session)
    await shift_service.finish_shift_automatically(context.application)
