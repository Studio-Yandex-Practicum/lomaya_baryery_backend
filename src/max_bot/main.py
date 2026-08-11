import asyncio
import logging
import os
import ssl
from contextlib import suppress
from typing import Optional
from urllib.parse import urljoin

import aiohttp
import aiomax
from aiolimiter import AsyncLimiter
from aiomax.exceptions import AiomaxException, InternalError

from src.bots.services import MessageSender, check_user_blocked, retry
from src.core.db import models
from src.core.settings import settings
from src.max_bot import ui
from src.max_bot.handlers import bot_stopped_handler, router
from src.max_bot.instance import get_max_bot, set_max_bot

# Лимит API Max - 30 запросов в секунду, оставляем запас
send_rate_limiter = AsyncLimiter(25, 1)


class MaxBot(aiomax.Bot, MessageSender):
    """Бот мессенджера Max.

    Дополняет aiomax обработкой события bot_stopped, нормализацией сообщений без текста
    и управлением жизненным циклом бота в режимах polling и webhook.

    Экземпляр создается только внутри запущенного event loop: aiohttp-сессия
    привязывается к текущему циклу событий. Экземпляр одноразовый - после stop()
    сессия закрыта, для нового запуска нужен новый экземпляр.
    """

    RETRIABLE_ERRORS = (aiohttp.ClientError, asyncio.TimeoutError, InternalError)
    SEND_ERRORS = (AiomaxException,)

    def __init__(self) -> None:
        super().__init__(settings.MAX_BOT_TOKEN, use_certificate=settings.MAX_BOT_USE_CERTIFICATE)
        if router.parent is not None:
            # роутер с обработчиками - модульный объект: чтобы его можно было
            # передать новому экземпляру бота, сначала отвязываем от предыдущего
            router.parent.remove_router(router)
        self.add_router(router)
        self.__polling_task: Optional[asyncio.Task] = None
        self.__webhook_mode = False
        self.session = self.__make_session()

    @classmethod
    async def start_bot(cls, webhook_mode: Optional[bool] = None) -> Optional["MaxBot"]:
        """Создать и запустить Max-бота. Возвращает None, если бот не настроен или не запустился."""
        if not settings.MAX_BOT_TOKEN:
            # проверка токена до создания экземпляра: конструктор уже открывает сессию
            logging.warning("MAX_BOT_TOKEN не задан - Max-бот не запущен.")
            return None
        bot = None
        try:
            bot = cls()
            await bot.start(webhook_mode)
        except Exception as e:
            logging.exception(f"Не удалось запустить Max-бота: {e}")
            if bot is not None:
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

    def is_user_blocked(self, user: models.User) -> bool:
        return user.max_blocked

    async def handle_send_error(self, user: models.User, error: AiomaxException) -> None:
        # импорт внутри метода: error_handler зависит от сервисов приложения,
        # которые импортируют src.bots.services
        from src.max_bot.error_handler import error_handler

        await error_handler(user, error)

    @check_user_blocked
    @retry()
    async def send_message_to_user(self, user: models.User, text: str) -> None:
        """Отправить участнику проекта текстовое сообщение.

        Имя отличается от send_message родительского класса: тот принимает chat_id/user_id
        и используется обработчиками бота для ответов в чате.
        """
        async with send_rate_limiter:
            await self.send_message(text, user_id=user.max_user_id)

    @check_user_blocked
    @retry()
    async def send_photo_to_user(self, user: models.User, photo: str, caption: str) -> None:
        """Отправить участнику проекта фото задания с клавиатурой ежедневного задания."""
        async with send_rate_limiter:
            await self.send_message(
                caption,
                user_id=user.max_user_id,
                attachments=aiomax.PhotoAttachment(url=photo),
                keyboard=ui.DAILY_TASK_KEYBOARD,
            )

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
        """Подписаться на обновления через webhook либо запустить polling."""
        self.__webhook_mode = settings.MAX_BOT_WEBHOOK_MODE if webhook_mode is None else webhook_mode
        await self.get_me()
        # режимы webhook и polling взаимоисключающие, поэтому старые подписки снимаются в обоих
        await self.__remove_subscriptions()
        if self.__webhook_mode:
            await self.post("subscriptions", json={"url": settings.max_webhook_url})
        else:
            self.__polling_task = asyncio.create_task(self.start_polling(session=self.session))

    async def stop(self) -> None:
        """Остановить получение обновлений и освободить ресурсы."""
        if self.__polling_task is not None:
            self.polling = False
            self.__polling_task.cancel()
            with suppress(asyncio.CancelledError):
                await self.__polling_task
            self.__polling_task = None
        elif self.__webhook_mode:
            with suppress(Exception):
                await self.delete("subscriptions", params={"url": settings.max_webhook_url})
        # start_polling закрывает сессию сам, но только если успел её принять:
        # отмененная сразу после запуска задача оставила бы сессию открытой
        await self.close_session()

    async def close_session(self) -> None:
        """Закрыть сессию, если она еще не закрыта."""
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
        """Создать aiohttp-сессию для API Max при инициализации бота.

        Собственную сессию aiomax создает только внутри start_polling, поэтому в режиме
        webhook её не было бы вовсе, а настройки TLS применялись бы лишь при polling.
        """
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
