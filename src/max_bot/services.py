import asyncio
import functools
import logging
from typing import Optional

import aiohttp
from aiolimiter import AsyncLimiter
from aiomax import PhotoAttachment
from aiomax.exceptions import AiomaxException, InternalError

from src.core.db import models
from src.max_bot.instance import get_max_bot

# Лимит API Max - 30 запросов в секунду, оставляем запас
send_rate_limiter = AsyncLimiter(25, 1)

RETRIABLE_ERRORS = (aiohttp.ClientError, asyncio.TimeoutError, InternalError)


def check_max_user_blocked(func):
    """Проверка блокировки пользователя перед отправкой сообщения."""

    @functools.wraps(func)
    async def _func_wrapper(*args, **kwargs):
        user = kwargs['user'] if 'user' in kwargs else args[0]
        if user.max_blocked:
            return
        await func(*args, **kwargs)

    return _func_wrapper


def retry(start_sleep_time: int = 3, max_attempt_number: int = 5):
    """Функция для повторного выполнения метода через некоторое время, если возникла ошибка."""

    def _func_wrapper(func):
        @functools.wraps(func)
        async def _inner(*args, **kwargs):
            user = kwargs['user'] if 'user' in kwargs else args[0]
            for n in range(max_attempt_number):
                try:
                    return await func(*args, **kwargs)
                except RETRIABLE_ERRORS as exc:
                    logging.exception(f"Сообщение пользователю {user} не было отправлено. Ошибка отправления: {exc}")
                    retry_delay = start_sleep_time * 3**n
                    await asyncio.sleep(retry_delay)
                    continue
                except AiomaxException as exc:
                    # импорт внутри функции: error_handler зависит от сервисов приложения,
                    # которые импортируют src.bot.services
                    from src.max_bot.error_handler import error_handler

                    return await error_handler(user, exc)

        return _inner

    return _func_wrapper


@check_max_user_blocked
@retry()
async def send_message(user: models.User, text: str) -> None:
    """Отправить пользователю текстовое сообщение через Max-бота."""
    bot = get_max_bot()
    if bot is None:
        logging.warning(f"Max-бот не запущен, сообщение пользователю {user} не отправлено.")
        return
    async with send_rate_limiter:
        await bot.send_message(text, user_id=user.max_user_id)


@check_max_user_blocked
@retry()
async def send_photo(user: models.User, photo_url: str, caption: str, keyboard: Optional[list] = None) -> None:
    """Отправить пользователю фото с подписью через Max-бота."""
    bot = get_max_bot()
    if bot is None:
        logging.warning(f"Max-бот не запущен, сообщение пользователю {user} не отправлено.")
        return
    async with send_rate_limiter:
        await bot.send_message(
            caption,
            user_id=user.max_user_id,
            attachments=PhotoAttachment(url=photo_url),
            keyboard=keyboard,
        )
