import asyncio
from datetime import datetime as dt
from typing import Optional

from telegram.ext import Application

from src.api.request_models.request import RequestDeclineRequest
from src.api.request_models.shift import ShiftCancelRequest
from src.core import settings
from src.core.db import models

FORMAT_PHOTO_DATE = "%d.%m.%Y"


class BotService:
    def __init__(self, telegram_bot: Application) -> None:
        self.__bot = telegram_bot.bot
        self.__bot_application = telegram_bot

    async def notify_approved_request(self, user: models.User) -> None:
        """Уведомление участника о решении по заявке в telegram.

        - Заявка принята.
        """
        text = f"Привет, {user.name} {user.surname}! Поздравляем, ты в проекте!"
        await self.__bot.send_message(user.telegram_id, text)

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
        await self.__bot.send_message(user.telegram_id, text)

    async def notify_approved_task(self, user: models.User, report: models.Report) -> None:
        """Уведомление участника о проверенном задании.

        - Задание принято, начислен 1 ломбарьерчик.
        """
        photo_date = dt.strftime(report.uploaded_at, FORMAT_PHOTO_DATE)
        text = (
            f"Твой отчет от {photo_date} принят! "
            f"Тебе начислен 1 \"ломбарьерчик\". "
            f"Следующее задание придет в 8.00 мск."
        )
        await self.__bot.send_message(user.telegram_id, text)

    async def notify_declined_task(self, user: models.User) -> None:
        """Уведомление участника о проверенном задании.

        - Задание не принято.
        """
        text = (
            "К сожалению, мы не можем принять твой фотоотчет! "
            "Возможно на фотографии не видно, что именно ты выполняешь задание. "
            "Предлагаем продолжить, ведь впереди много интересных заданий. "
            "Следующее задание придет в 8.00 мск."
        )
        await self.__bot.send_message(user.telegram_id, text)

    async def notify_excluded_members(self, members: list[models.Member]) -> None:
        """Уведомляет участников об исключении из смены."""
        text = (
            "К сожалению, мы заблокировали Ваше участие в смене из-за неактивности - "
            "Вы не отправили ни одного отчета на несколько последних заданий подряд. "
            "Вы не сможете получать новые задания, но всё еще можете потратить свои накопленные ломбарьерчики. "
            "Если Вы считаете, что произошла ошибка - обращайтесь "
            f"за помощью на электронную почту {settings.ORGANIZATIONS_EMAIL}."
        )
        send_message_tasks = [self.__bot.send_message(member.user.telegram_id, text) for member in members]
        self.__bot_application.create_task(asyncio.gather(*send_message_tasks))

    async def notify_that_shift_is_finished(self, shift: models.Shift) -> None:
        """Уведомляет активных участников об окончании смены."""
        send_message_tasks = [
            self.__bot.send_message(
                member.user.telegram_id,
                shift.final_message.format(
                    name=member.user.name, surname=member.user.surname, numbers_lombaryers=member.numbers_lombaryers
                ),
            )
            for member in shift.members
        ]
        self.__bot_application.create_task(asyncio.gather(*send_message_tasks))

    async def notify_that_shift_is_cancelled(self, shift: models.Shift, notice: Optional[ShiftCancelRequest]) -> None:
        """Уведомляет пользователей об отмене смены."""
        text = "Смена отменена"
        if notice:
            text = notice.message
        send_message_tasks = [self.__bot.send_message(request.user.telegram_id, text) for request in shift.requests]
        self.__bot_application.create_task(asyncio.gather(*send_message_tasks))
