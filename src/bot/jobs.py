from telegram import ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from src.bot.api_services import get_report_service_callback


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
    report_service = await get_report_service_callback()
    await report_service.check_members_activity(context.bot)
    reports = await report_service.get_today_active_reports()
    for task in reports:
        await context.bot.send_photo(
            chat_id=task.user_telegram_id,
            photo=task.task_url,
            caption=(
                f"Сегодня твоим заданием будет {task.task_description}."
                f"Не забудь сделать фотографию, как ты выполняешь задание, и отправить на проверку."
            ),
            reply_markup=buttons,
        )
