from telegram.ext import ApplicationBuilder, CommandHandler

from src.bot.handlers import start
from src.core.settings import BOT_TOKEN

bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
