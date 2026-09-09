import asyncio
import logging
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from telegram import ReplyKeyboardMarkup
from telegram.error import (
    BadRequest,
    Forbidden,
    NetworkError,
    RetryAfter,
    TelegramError,
    TimedOut,
)
from telegram.ext import Application

from src.api.request_models.request import RequestDeclineRequest
from src.api.request_models.user import DATE_FORMAT
from src.bot.max.instance import get_max_bot
from src.bot.services import MessageSender, check_user_blocked, retry
from src.core.db import models
from src.core.settings import settings
from src.core.utils import (
    get_current_task_date,
    get_lombaryers_for_quantity,
    get_message_with_numbers_attempts,
)

if TYPE_CHECKING:
    from src.bot.max.main import MaxBot


class BotService(MessageSender):
    RETRIABLE_ERRORS = (RetryAfter, TimedOut, NetworkError)
    # BadRequest наследуется от NetworkError, но означает ошибку в самом запросе:
    # повтор не поможет, а недоступный чат так и не был бы отмечен блокировкой
    NON_RETRIABLE_ERRORS = (BadRequest,)
    SEND_ERRORS = (TelegramError,)
    # У telegram о блокировке говорит не тип ошибки, а её текст
    BLOCKING_ERROR_MESSAGES = {
        BadRequest: ("Chat not found",),
        Forbidden: ("Forbidden: bot was blocked by the user",),
    }

    def __init__(self, telegram_bot: Application, max_bot: Optional["MaxBot"] = None) -> None:
        self.__bot = telegram_bot.bot
        self.__bot_application = telegram_bot
        # Max-бот необязателен: если он не запущен, участники из Max уведомления не получат,
        # но отправка участникам из telegram продолжит работать
        self.__max_bot = max_bot if max_bot is not None else get_max_bot()

    def is_blocking_error(self, error: TelegramError) -> bool:
        return error.message in self.BLOCKING_ERROR_MESSAGES.get(type(error), ())

    @check_user_blocked
    @retry()
    async def send_message(self, user: models.User, text: str) -> None:
        if user.max_user_id is None:
            await self.__bot.send_message(user.telegram_id, text)
        elif self.__max_bot is not None:
            await self.__max_bot.send_message_to_user(user, text)
        else:
            logging.warning(f"Max-бот не запущен, сообщение пользователю {user} не отправлено.")

    @check_user_blocked
    @retry()
    async def send_photo(self, user: models.User, photo: str, caption: str, reply_markup: ReplyKeyboardMarkup) -> None:
        if user.max_user_id is None:
            await self.__bot.send_photo(
                chat_id=user.telegram_id, photo=photo, caption=caption, reply_markup=reply_markup
            )
        elif self.__max_bot is not None:
            await self.__max_bot.send_photo_to_user(user, photo, caption)
        else:
            logging.warning(f"Max-бот не запущен, задание пользователю {user} не отправлено.")

    async def notify_approved_request(self, user: models.User, first_task_date: str) -> None:
        """Уведомление участника о решении по заявке в telegram.

        - Заявка принята.
        """
        text = (
            f"Привет, {user.name} {user.surname}! Поздравляем, ты в проекте! "
            f"{first_task_date} в {settings.FORMATTED_TASK_TIME} часов утра "
            "тебе поступит первое задание."
        )
        await self.send_message(user, text)

    async def notify_declined_request(
        self, user: models.User, decline_request_data: RequestDeclineRequest | None
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
        await self.send_message(user, text)

    async def notify_approved_task(self, user: models.User, report: models.Report, shift: models.Shift) -> None:
        """Уведомление участника о проверенном задании.

        - Задание принято, начислен 1 ломбарьерчик.
        """
        photo_date = datetime.strftime(report.uploaded_at, DATE_FORMAT)
        text = f"Твой отчет от {photo_date} принят! Тебе начислен 1 \"ломбарьерчик\". "
        if date.today() < shift.finished_at:
            text = text + f"Следующее задание придет в {settings.FORMATTED_TASK_TIME} часов утра."
        await self.send_message(user, text)

    async def notify_declined_task(self, user: models.User, shift: models.Shift, report: models.Report) -> None:
        """Уведомление участника о проверенном задании.

        - Задание не принято.
        """
        text = (
            f"К сожалению, мы не можем принять твой фотоотчет от {report.uploaded_at.strftime(DATE_FORMAT)}! "
            "Возможно на фотографии не видно, что именно ты выполняешь задание. "
        )
        if date.today() < shift.finished_at and report.task_date == get_current_task_date():
            count_attempts = settings.NUMBER_ATTEMPTS_SUBMIT_REPORT - report.number_attempt
            text += get_message_with_numbers_attempts(count_attempts)
        await self.send_message(user, text)

    async def notify_excluded_members(self, members: list[models.Member]) -> None:
        """Уведомляет участников об исключении из смены."""
        text = (
            "К сожалению, мы заблокировали Ваше участие в смене из-за неактивности - "
            "Вы не отправили ни одного отчета на несколько последних заданий подряд. "
            "Вы не сможете получать новые задания, но всё еще можете потратить свои накопленные ломбарьерчики. "
            "Если Вы считаете, что произошла ошибка - обращайтесь "
            f"за помощью на электронную почту {settings.ORGANIZATIONS_EMAIL}."
        )
        send_message_tasks = [self.send_message(member.user, text) for member in members]
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
            )
            for member in shift.members
        ]
        self.__bot_application.create_task(asyncio.gather(*send_message_tasks))

    async def notify_that_shift_is_cancelled(self, users: list[models.User], final_message: str) -> None:
        """Уведомляет пользователей об отмене смены."""
        send_message_tasks = [self.send_message(user, final_message) for user in users]
        self.__bot_application.create_task(asyncio.gather(*send_message_tasks))

    async def notify_that_shift_start_date_is_changed(
        self, users: list[models.User], start_date_changed_message: str
    ) -> None:
        """Уведомляет пользователей о переносе даты старта смены."""
        send_message_tasks = [self.send_message(user, start_date_changed_message) for user in users]
        self.__bot_application.create_task(asyncio.gather(*send_message_tasks))
