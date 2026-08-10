import asyncio
import logging
import os
import ssl
from contextlib import suppress
from typing import Optional
from urllib.parse import urljoin

import aiohttp
import aiomax

from src.core.settings import settings
from src.max_bot.handlers import bot_stopped_handler, router
from src.max_bot.instance import get_max_bot, set_max_bot


class MaxBot(aiomax.Bot):
    """Бот мессенджера Max.

    Дополняет aiomax обработкой события bot_stopped, нормализацией сообщений без текста
    и управлением жизненным циклом бота в режимах polling и webhook.
    """

    def __init__(self) -> None:
        super().__init__(settings.MAX_BOT_TOKEN, use_certificate=settings.MAX_BOT_USE_CERTIFICATE)
        if router.parent is not None:
            # роутер с обработчиками - модульный объект: чтобы его можно было
            # передать новому экземпляру бота, сначала отвязываем от предыдущего
            router.parent.remove_router(router)
        self.add_router(router)
        self.__polling_task: Optional[asyncio.Task] = None
        self.__webhook_mode = False

    @classmethod
    async def start_bot(cls, webhook_mode: Optional[bool] = None) -> Optional["MaxBot"]:
        """Создать и запустить Max-бота. Возвращает None, если бот не настроен или не запустился."""
        if not settings.MAX_BOT_TOKEN:
            logging.warning("MAX_BOT_TOKEN не задан - Max-бот не запущен.")
            return None
        bot = cls()
        try:
            await bot.start(webhook_mode)
        except Exception as e:
            logging.exception(f"Не удалось запустить Max-бота: {e}")
            await bot.close_session()
            return None
        set_max_bot(bot)
        return bot

    @classmethod
    async def stop_bot(cls) -> None:
        """Остановить запущенного Max-бота."""
        bot = get_max_bot()
        if bot is None:
            return
        await bot.stop()
        set_max_bot(None)

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

    async def start(self, webhook_mode: Optional[bool] = None) -> None:
        """Открыть сессию и подписаться на обновления через webhook либо запустить polling."""
        self.__webhook_mode = settings.MAX_BOT_WEBHOOK_MODE if webhook_mode is None else webhook_mode
        session = self.__make_session()
        self.session = session
        await self.get_me()
        # режимы webhook и polling взаимоисключающие, поэтому старые подписки снимаются в обоих
        await self.__remove_subscriptions()
        if self.__webhook_mode:
            await self.post("subscriptions", json={"url": settings.max_webhook_url})
        else:
            self.__polling_task = asyncio.create_task(self.start_polling(session=session))

    async def stop(self) -> None:
        """Остановить получение обновлений и освободить ресурсы."""
        if self.__polling_task is not None:
            self.polling = False
            self.__polling_task.cancel()
            with suppress(asyncio.CancelledError):
                await self.__polling_task
            # сессию закрывает сам start_polling при выходе из цикла
            self.__polling_task = None
            return
        if self.__webhook_mode:
            with suppress(Exception):
                await self.delete("subscriptions", params={"url": settings.max_webhook_url})
        await self.close_session()

    async def close_session(self) -> None:
        """Закрыть сессию, если она была открыта."""
        if self.session is not None:
            await self.session.close()
            self.session = None

    async def get(self, url: str, *args, **kwargs):
        return await super().get(self.__absolute_url(url), *args, **kwargs)

    async def post(self, url: str, *args, **kwargs):
        return await super().post(self.__absolute_url(url), *args, **kwargs)

    async def put(self, url: str, *args, **kwargs):
        return await super().put(self.__absolute_url(url), *args, **kwargs)

    async def patch(self, url: str, *args, **kwargs):
        return await super().patch(self.__absolute_url(url), *args, **kwargs)

    async def delete(self, url: str, *args, **kwargs):
        return await super().delete(self.__absolute_url(url), *args, **kwargs)

    def __absolute_url(self, url: str) -> str:
        """Привести относительный путь API Max к абсолютному URL.

        aiomax обращается к API относительными путями ("me", "messages"), но aiohttp
        поддерживает такие пути вместе с base_url только с версии 3.11.
        """
        return url if "://" in url else urljoin(self.api_url, url)

    def __make_session(self) -> aiohttp.ClientSession:
        """Создать aiohttp-сессию для API Max (aiomax создает её сам только внутри start_polling)."""
        connector = None
        if self.use_certificate:
            certificate_path = os.path.join(os.path.dirname(aiomax.__file__), "russian_trusted_root_ca.cer")
            ssl_context = ssl.create_default_context()
            ssl_context.load_verify_locations(cafile=certificate_path)
            connector = aiohttp.TCPConnector(ssl=ssl_context)
        return aiohttp.ClientSession(headers={"Authorization": self.access_token}, connector=connector)

    async def __remove_subscriptions(self) -> None:
        """Снять все webhook-подписки бота."""
        response = await self.get("subscriptions")
        subscriptions = (await response.json()).get("subscriptions", [])
        for subscription in subscriptions:
            await self.delete("subscriptions", params={"url": subscription["url"]})
