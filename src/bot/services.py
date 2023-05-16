import asyncio
import functools
import logging
from datetime import date, datetime

from telegram import ReplyKeyboardMarkup
from telegram.error import NetworkError, RetryAfter, TelegramError, TimedOut
from telegram.ext import Application

from src.api.request_models.request import RequestDeclineRequest
from src.bot.error_handler import error_handler
from src.core.db import models
from src.core.services.history_message_service import MessageHistoryService
from src.core.settings import settings
from src.core.utils import get_lombaryers_for_quantity

FORMAT_PHOTO_DATE = "%d.%m.%Y"


def check_user_blocked(func):
    """Проверка блокировки пользователя перед отправкой сообщения."""

    @functools.wraps(func)
    async def _func_wrapper(*args, **kwargs):
        user = kwargs['user'] if 'user' in kwargs else args[1]
        if user.telegram_blocked:
            return
        await func(*args, **kwargs)

    return _func_wrapper


def retry(start_sleep_time: int = 3, max_attempt_number: int = 5):
    """Функция для повторного выполнения метода через некоторое время, если возникла ошибка."""

    def _func_wrapper(func):
        @functools.wraps(func)
        async def _inner(*args, **kwargs):
            user = kwargs['user'] if 'user' in kwargs else args[1]
            for n in range(max_attempt_number):
                try:
                    return await func(*args, **kwargs)
                except (RetryAfter, TimedOut, NetworkError) as exc:
                    logging.exception(f"Сообщение пользователю {user} не было отправлено. Ошибка отправления: {exc}")
                    retry_delay = start_sleep_time * 3**n
                    await asyncio.sleep(retry_delay)
                    continue
                except TelegramError as exc:
                    return await error_handler(user, exc)

        return _inner

    return _func_wrapper


class BotService:
    def __init__(self, telegram_bot: Application, history_service: MessageHistoryService) -> None:
        self.__bot = telegram_bot.bot
        self.__bot_application = telegram_bot
        self.__history_service = history_service

    @check_user_blocked
    @retry()
    async def send_message(
        self, user: models.User, text: str, event: models.MessageHistory.Event, shift_id=None
    ) -> None:
        message = await self.__bot.send_message(user.telegram_id, text)
        await self.__history_service.create_history_message(user.id, message.message_id, text, event, shift_id)

    @check_user_blocked
    @retry()
    async def send_photo(
        self,
        user: models.User,
        photo: str,
        caption: str,
        reply_markup: ReplyKeyboardMarkup,
        event: models.MessageHistory.Event,
        shift_id: models.Shift | None,
    ) -> None:
        message = await self.__bot.send_photo(
            chat_id=user.telegram_id, photo=photo, caption=caption, reply_markup=reply_markup
        )
        await self.__history_service.create_history_message(user.id, message.message_id, caption, event, shift_id)

    async def notify_approved_request(self, user: models.User, first_task_date: str, shift_id: int) -> None:
        """Уведомление участника о решении по заявке в telegram.

        - Заявка принята.
        """
        text = (
            f"Привет, {user.name} {user.surname}! Поздравляем, ты в проекте! "
            f"{first_task_date} в {settings.formatted_task_time} часов утра "
            "тебе поступит первое задание."
        )
        event = models.MessageHistory.Event.REQUEST_ACCEPTED
        await self.send_message(user, text, event, shift_id)

    async def notify_declined_request(
        self, user: models.User, decline_request_data: RequestDeclineRequest | None, shift_id: int
    ) -> None:
        """Уведомление участника о решении по заявке в telegram.

        - Заявка отклонена.
        """
        if decline_request_data and decline_request_data.message:
            text = decline_request_data.message
        else:
            text = (
                f"К сожалению, на данный момент мы не можем зарегистрировать вас"
                f" в проекте. Вы можете написать на почту "
                f"{settings.ORGANIZATIONS_EMAIL}. Чтобы не пропустить актуальные"
                f" новости Центра \"Ломая барьеры\" - вступайте в нашу группу "
                f"{settings.ORGANIZATIONS_GROUP}"
            )
        event = models.MessageHistory.Event.REQUEST_CANCELED
        await self.send_message(user, text, event, shift_id)

    async def notify_approved_task(self, user: models.User, report: models.Report, shift: models.Shift) -> None:
        """Уведомление участника о проверенном задании.

        - Задание принято, начислен 1 ломбарьерчик.
        """
        photo_date = datetime.strftime(report.uploaded_at, FORMAT_PHOTO_DATE)
        text = f"Твой отчет от {photo_date} принят! Тебе начислен 1 \"ломбарьерчик\". "
        if date.today() < shift.finished_at:
            text = text + f"Следующее задание придет в {settings.formatted_task_time} часов утра."
        event = models.MessageHistory.Event.TASK_ACCEPTED
        await self.send_message(user, text, event, shift.id)

    async def notify_declined_task(self, user: models.User, shift: models.Shift) -> None:
        """Уведомление участника о проверенном задании.

        - Задание не принято.
        """
        text = (
            "К сожалению, мы не можем принять твой фотоотчет! "
            "Возможно на фотографии не видно, что именно ты выполняешь задание. "
        )
        if date.today() < shift.finished_at:
            text = text + f"Ты можешь отправить отчет повторно до {settings.formatted_task_time} часов утра."
        event = models.MessageHistory.Event.TASK_NOT_ACCEPTED
        await self.send_message(user, text, event, shift.id)

    async def notify_excluded_members(self, members: list[models.Member], shift_id: int) -> None:
        """Уведомляет участников об исключении из смены."""
        text = (
            "К сожалению, мы заблокировали Ваше участие в смене из-за неактивности - "
            "Вы не отправили ни одного отчета на несколько последних заданий подряд. "
            "Вы не сможете получать новые задания, но всё еще можете потратить свои накопленные ломбарьерчики. "
            "Если Вы считаете, что произошла ошибка - обращайтесь "
            f"за помощью на электронную почту {settings.ORGANIZATIONS_EMAIL}."
        )
        event = models.MessageHistory.Event.EXCLUDE_FROM_SHIFT
        send_message_tasks = [self.send_message(member.user, text, event, shift_id) for member in members]
        self.__bot_application.create_task(asyncio.gather(*send_message_tasks))

    async def notify_that_shift_is_finished(self, shift: models.Shift) -> None:
        """Уведомляет активных участников об окончании смены."""
        send_message_tasks = [
            self.send_message(
                member.user,
                shift.final_message.format(
                    name=member.user.name,
                    surname=member.user.surname,
                    numbers_lombaryers=member.numbers_lombaryers,
                    lombaryers_case=get_lombaryers_for_quantity(member.numbers_lombaryers),
                ),
                models.MessageHistory.Event.SHIFT_ENDED,
                shift.id,
            )
            for member in shift.members
        ]
        self.__bot_application.create_task(asyncio.gather(*send_message_tasks))

    async def notify_that_shift_is_cancelled(self, users: list[models.User], final_message: str, shift_id: int) -> None:
        """Уведомляет пользователей об отмене смены."""
        event = models.MessageHistory.Event.SHIFT_CANCELED
        send_message_tasks = [self.send_message(user, final_message, event, shift_id) for user in users]
        self.__bot_application.create_task(asyncio.gather(*send_message_tasks))

    async def notify_that_shift_start_date_is_changed(
        self, users: list[models.User], start_date_changed_message: str, shift_id: int
    ) -> None:
        """Уведомляет пользователей о переносе даты старта смены."""
        event = models.MessageHistory.Event.START_SHIFT_CHANGED
        send_message_tasks = [self.send_message(user, start_date_changed_message, event, shift_id) for user in users]
        self.__bot_application.create_task(asyncio.gather(*send_message_tasks))
