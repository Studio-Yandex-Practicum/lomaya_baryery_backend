from telegram.ext import CallbackContext


async def send_no_report_reminder_job(context: CallbackContext) -> None:
    """Отправить напоминание об отчёте."""
    await context.bot.send_message(
        chat_id='5702444617',  # заменить на user.telegram_id
        text=(
            f"<user.name> <user.surname>, мы потеряли тебя! Напоминаем, "  # добавить user.name и user.surname
            f"что за каждое выполненное задание ты получаешь виртуальные "
            f"«ломбарьерчики», которые можешь обменять на призы и подарки!"
        )
    )
