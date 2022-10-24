from telegram import ReplyKeyboardMarkup
from telegram.ext import CallbackContext


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


async def send_task_job(context: CallbackContext, telegram_id: int, description: str, task_url: str) -> None:
    buttons = ReplyKeyboardMarkup([["Пропустить задание", "Баланс ломбарьеров"]], resize_keyboard=True)
    await context.bot.send_message(chat_id=telegram_id, text=(task_url))
    await context.bot.send_message(
        chat_id=telegram_id,
        text=(
            f"Сегодня твоим заданием будет {description}."
            f"Не забудь сделать фотографию, как ты выполняешь задание, и отправить на проверку."
        ),
        reply_markup=buttons,
    )
