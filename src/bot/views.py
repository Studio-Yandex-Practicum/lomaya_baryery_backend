import telebot

from src.core.settings import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['hello'])
def command_hello(message):
    bot.send_message(message.chat.id, "Hello world!!!")
