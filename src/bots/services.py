import asyncio
import functools
import logging

from src.core.db import models


class MessageSender:
    """Контракт для классов, отправляющих сообщения участникам через мессенджер.

    Определяет то, что зависит от мессенджера, и позволяет использовать
    декораторы check_user_blocked и retry для любого из ботов.
    """

    # Ошибки мессенджера, при которых отправку имеет смысл повторить
    RETRIABLE_ERRORS: tuple = ()
    # Ошибки мессенджера, которые обрабатываются без повторной отправки
    SEND_ERRORS: tuple = ()

    def is_user_blocked(self, user: models.User) -> bool:
        """Проверить, заблокировал ли пользователь бота этого мессенджера."""
        raise NotImplementedError

    async def handle_send_error(self, user: models.User, error: Exception) -> None:
        """Обработать ошибку отправки, не требующую повтора."""
        raise NotImplementedError


def check_user_blocked(func):
    """Проверка блокировки пользователя перед отправкой сообщения."""

    @functools.wraps(func)
    async def _func_wrapper(self: MessageSender, user: models.User, *args, **kwargs):
        if self.is_user_blocked(user):
            return
        return await func(self, user, *args, **kwargs)

    return _func_wrapper


def retry(start_sleep_time: int = 3, max_attempt_number: int = 5):
    """Функция для повторного выполнения метода через некоторое время, если возникла ошибка."""

    def _func_wrapper(func):
        @functools.wraps(func)
        async def _inner(self: MessageSender, user: models.User, *args, **kwargs):
            for n in range(max_attempt_number):
                try:
                    return await func(self, user, *args, **kwargs)
                except self.RETRIABLE_ERRORS as exc:
                    logging.exception(f"Сообщение пользователю {user} не было отправлено. Ошибка отправления: {exc}")
                    retry_delay = start_sleep_time * 3**n
                    await asyncio.sleep(retry_delay)
                    continue
                except self.SEND_ERRORS as exc:
                    return await self.handle_send_error(user, exc)

        return _inner

    return _func_wrapper
