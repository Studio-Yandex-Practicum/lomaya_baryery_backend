import asyncio
import logging
import os
import ssl
from contextlib import suppress
from typing import Optional

import aiohttp
import aiomax

from src.core.settings import settings
from src.max_bot.handlers import bot_stopped_handler, router
from src.max_bot.instance import get_max_bot, set_max_bot

_polling_task: Optional[asyncio.Task] = None


class MaxBot(aiomax.Bot):
    """Бот Max с обработкой события bot_stopped и нормализацией сообщений без текста."""

    async def handle_update(self, update: dict) -> None:
        if update.get("update_type") == "bot_stopped":
            # aiomax молча игнорирует bot_stopped, поэтому обрабатываем его самостоятельно
            await bot_stopped_handler(update)
            return
        message = update.get("message")
        if message and message.get("body") and message["body"].get("text") is None:
            # у сообщений без текста (например, только с фото) body.text = null,
            # что роняет разбор команд в aiomax
            message["body"]["text"] = ""
        await super().handle_update(update)


def create_max_bot() -> MaxBot:
    bot = MaxBot(settings.MAX_BOT_TOKEN, use_certificate=settings.MAX_BOT_USE_CERTIFICATE)
    bot.add_router(router)
    return bot


def _make_session(bot: MaxBot) -> aiohttp.ClientSession:
    """Создать aiohttp-сессию для API Max (aiomax создает её сам только внутри start_polling)."""
    connector = None
    if bot.use_certificate:
        certificate_path = os.path.join(os.path.dirname(aiomax.__file__), "russian_trusted_root_ca.cer")
        ssl_context = ssl.create_default_context()
        ssl_context.load_verify_locations(cafile=certificate_path)
        connector = aiohttp.TCPConnector(ssl=ssl_context)
    return aiohttp.ClientSession(
        headers={"Authorization": bot.access_token},
        connector=connector,
        base_url=bot.api_url,
    )


async def _remove_subscriptions(bot: MaxBot) -> None:
    """Снять все webhook-подписки: режимы webhook и polling взаимоисключающие."""
    response = await bot.get("subscriptions")
    subscriptions = (await response.json()).get("subscriptions", [])
    for subscription in subscriptions:
        await bot.delete("subscriptions", params={"url": subscription["url"]})


async def start_max_bot(webhook_mode: Optional[bool] = None) -> Optional[MaxBot]:
    """Запустить Max-бота в режиме polling или webhook. Возвращает None, если бот не настроен."""
    global _polling_task
    if not settings.MAX_BOT_TOKEN:
        logging.warning("MAX_BOT_TOKEN не задан - Max-бот не запущен.")
        return None
    if webhook_mode is None:
        webhook_mode = settings.MAX_BOT_WEBHOOK_MODE
    bot = create_max_bot()
    session = _make_session(bot)
    try:
        bot.session = session
        await bot.get_me()
        if webhook_mode:
            await _remove_subscriptions(bot)
            await bot.post("subscriptions", json={"url": settings.max_webhook_url})
        else:
            await _remove_subscriptions(bot)
            _polling_task = asyncio.create_task(bot.start_polling(session=session))
    except Exception as e:
        logging.exception(f"Не удалось запустить Max-бота: {e}")
        await session.close()
        return None
    set_max_bot(bot)
    return bot


async def stop_max_bot() -> None:
    """Остановить Max-бота и освободить ресурсы."""
    global _polling_task
    max_bot = get_max_bot()
    if max_bot is None:
        return
    if _polling_task is not None:
        max_bot.polling = False
        _polling_task.cancel()
        with suppress(asyncio.CancelledError):
            await _polling_task
    elif max_bot.session is not None:
        if settings.MAX_BOT_WEBHOOK_MODE:
            with suppress(Exception):
                await max_bot.delete("subscriptions", params={"url": settings.max_webhook_url})
        await max_bot.session.close()
    set_max_bot(None)
    _polling_task = None
