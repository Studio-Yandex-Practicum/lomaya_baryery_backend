from telegram import Update
from telegram.ext import CallbackContext


async def test(context: CallbackContext) -> None:
    """
    Send test message after running
    :param context: CallbackContext
    """
    chat_id = "1111"
    await context.bot.send_message(chat_id=chat_id, text="Bot still running.")


async def start(update: Update, context: CallbackContext) -> None:
    """Команда /start."""
    start_text = (
        'Это бот Центра "Ломая барьеры", который в игровой форме поможет '
        'особенному ребенку стать немного самостоятельнее! Выполняя задания '
        'каждый день, ребенку будут начислять виртуальные "ломбарьерчики". '
        'Каждый месяц мы будем подводить итоги '
        'и награждать самых активных и старательных ребят!'
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=start_text
    )
