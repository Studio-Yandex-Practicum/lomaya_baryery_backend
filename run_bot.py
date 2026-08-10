from telegram.ext import Application

from src.bot.main import create_bot
from src.max_bot.main import start_max_bot, stop_max_bot


async def start_additional_bots(_: Application) -> None:
    """Запустить ботов дополнительных мессенджеров."""
    await start_max_bot(webhook_mode=False)


async def stop_additional_bots(_: Application) -> None:
    """Остановить ботов дополнительных мессенджеров."""
    await stop_max_bot()


if __name__ == '__main__':
    bot = create_bot()
    bot.post_init = start_additional_bots
    bot.post_shutdown = stop_additional_bots
    bot.run_polling()
