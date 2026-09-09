"""Запуск telegram- и Max-ботов без основного приложения.

Оба бота работают только в режиме polling: telegram поднимается через create_bot(),
Max - в его post_init/post_shutdown. Для разработки и тестирования ботов без API.
"""
from telegram.ext import Application

from src.bot.max.main import MaxBot
from src.bot.telegram.main import create_bot


async def start_additional_bots(_: Application) -> None:
    """Запустить ботов дополнительных мессенджеров."""
    await MaxBot.start_bot(webhook_mode=False)


async def stop_additional_bots(_: Application) -> None:
    """Остановить ботов дополнительных мессенджеров."""
    await MaxBot.stop_bot()


if __name__ == '__main__':
    bot = create_bot()
    bot.post_init = start_additional_bots
    bot.post_shutdown = stop_additional_bots
    bot.run_polling()
