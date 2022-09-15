from telegram import Update
from telegram.ext import CallbackContext


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
