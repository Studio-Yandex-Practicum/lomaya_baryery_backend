from telegram import Update
from telegram.ext import (Application, ApplicationBuilder, CommandHandler,
                          CallbackContext)
from src.core.settings import BOT_TOKEN
from src.main import app


async def test(context: CallbackContext) -> None:
    """
    Send test message after running
    :param context: CallbackContext
    """
    chat_id = "1111"
    await context.bot.send_message(chat_id=chat_id, text="Bot still running.")


async def start(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Привет! Я постараюсь помочь вам.")


def create_bot():
    """
    Create telegram bot application
    :return: Created telegram bot application
    """
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    # bot_app.job_queue.run_repeating(test, config.TEST_PERIOD)
    return bot_app


@app.on_event("startup")
async def init_polling() -> None:
    """
    Init bot polling
    :return: Initiated application
    """
    bot_app = create_bot()
    bot_app.run_polling()


