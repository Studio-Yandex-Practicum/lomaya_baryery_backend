import asyncio
import functools
import logging

from src.core.db import models


class MessageSender:
    """Контракт для классов, отправляющих сообщения участникам через мессенджер.

    Определяет то, что зависит от мессенджера, и позволяет использовать
    декораторы check_user_blocked и retry, а также общий error_handler
    для любого из ботов.
    """

    # Ошибки мессенджера, при которых отправку имеет смысл повторить
    RETRIABLE_ERRORS: tuple = ()
    # Подклассы RETRIABLE_ERRORS, повторять отправку при которых смысла нет
    NON_RETRIABLE_ERRORS: tuple = ()
    # Ошибки мессенджера, которые обрабатываются без повторной отправки
    SEND_ERRORS: tuple = ()
    # Ошибки мессенджера, означающие, что пользователь заблокировал бота
    BLOCKING_ERRORS: tuple = ()

    def is_retriable_error(self, error: Exception) -> bool:
        """Проверить, имеет ли смысл повторить отправку после ошибки."""
        return isinstance(error, self.RETRIABLE_ERRORS) and not isinstance(error, self.NON_RETRIABLE_ERRORS)

    def is_blocking_error(self, error: Exception) -> bool:
        """Проверить, означает ли ошибка отправки, что пользователь заблокировал бота."""
        return isinstance(error, self.BLOCKING_ERRORS)

    async def handle_send_error(self, user: models.User, error: Exception) -> None:
        """Обработать ошибку отправки, не требующую повтора."""
        # импорт внутри метода: error_handler зависит от сервисов приложения,
        # которые импортируют этот модуль
        from src.bots.error_handler import error_handler

        await error_handler(self, user, error)


def check_user_blocked(func):
    """Проверка блокировки пользователя перед отправкой сообщения."""

    @functools.wraps(func)
    async def _func_wrapper(self: MessageSender, user: models.User, *args, **kwargs):
        if user.is_blocked:
            return None
        return await func(self, user, *args, **kwargs)

    return _func_wrapper


def retry(start_sleep_time: int = 3, max_attempt_number: int = 5):
    """Функция для повторного выполнения метода через некоторое время, если возникла ошибка.

    Повторяются только ошибки, которые сендер считает временными: остальные сразу уходят
    в handle_send_error. Одним блоком except перехватываются оба набора ошибок, потому что
    в мессенджерах временные и постоянные ошибки бывают классами одной иерархии.
    """

    def _func_wrapper(func):
        @functools.wraps(func)
        async def _inner(self: MessageSender, user: models.User, *args, **kwargs):
            for n in range(max_attempt_number):
                try:
                    return await func(self, user, *args, **kwargs)
                except (*self.RETRIABLE_ERRORS, *self.SEND_ERRORS) as exc:
                    if not self.is_retriable_error(exc):
                        return await self.handle_send_error(user, exc)
                    logging.exception(f"Сообщение пользователю {user} не было отправлено. Ошибка отправления: {exc}")
                    retry_delay = start_sleep_time * 3**n
                    await asyncio.sleep(retry_delay)
            # попытки исчерпаны, ошибки каждой из них записаны в лог выше
            return None

        return _inner

    return _func_wrapper
