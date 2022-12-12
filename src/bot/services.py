from datetime import datetime as dt

from telegram.ext import Application

from src.api.request_models.request import RequestDeclineRequest
from src.core import settings
from src.core.db import models

FORMAT_PHOTO_DATE = "%d.%m.%Y"


class BotService:
    def __init__(self, telegram_bot: Application.bot) -> None:
        self.__bot = telegram_bot

    async def notify_approved_request(self, user: models.User) -> None:
        """Уведомление участника о решении по заявке в telegram.

        - Заявка принята.
        """
        text = f"Привет, {user.name} {user.surname}! Поздравляем, ты в проекте!"
        await self.__bot.send_message(user.telegram_id, text)

    async def notify_declined_request(self, user: models.User, decline_request_data: RequestDeclineRequest) -> None:
        """Уведомление участника о решении по заявке в telegram.

        - Заявка отклонена.
        """
        text = decline_request_data.message
        if not text:
            text = (
                f"К сожалению, на данный момент мы не можем зарегистрировать вас"
                f" в проекте. Вы можете написать на почту "
                f"{settings.ORGANIZATIONS_EMAIL}. Чтобы не пропустить актуальные"
                f" новости Центра \"Ломая барьеры\" - вступайте в нашу группу "
                f"{settings.ORGANIZATIONS_GROUP}"
            )
        await self.__bot.send_message(user.telegram_id, text)

    async def notify_approved_task(self, report: models.Report) -> None:
        """Уведомление участника о проверенном задании.

        - Задание принято, начислен 1 ломбарьерчик.
        """
        photo_date = dt.strftime(report.photo.created_at, FORMAT_PHOTO_DATE)
        text = (
            f"Твой отчет от {photo_date} принят! "
            f"Тебе начислен 1 \"ломбарьерчик\". "
            f"Следуюее задание придет в 8.00 мск."
        )
        await self.__bot.send_message(report.user.telegram_id, text)

    async def notify_declined_task(self, telegram_id: str) -> None:
        """Уведомление участника о проверенном задании.

        - Задание не принято.
        """
        text = (
            "К сожалению, мы не можем принять твой фотоотчет! "
            "Возможно на фотографии не видно, что именно ты выполняешь задание. "
            "Предлагаем продолжить, ведь впереди много интересных заданий. "
            "Следующее задание придет в 8.00 мск."
        )
        await self.__bot.send_message(telegram_id, text)

    async def notify_excluded_member(self, user: models.User) -> None:
        """Уведомляет участника об исключении из смены."""
        text = (
            "К сожалению, мы заблокировали Ваше участие в смене из-за неактивности - "
            "Вы не отправили ни одного отчета на несколько последних заданий подряд. "
            "Вы не сможете получать новые задания, но всё еще можете потратить свои накопленные ломбарьерчики. "
            "Если Вы считаете, что произошла ошибка - обращайтесь "
            f"за помощью на электронную почту {settings.ORGANIZATIONS_EMAIL}."
        )
        await self.__bot.send_message(user.telegram_id, text)

    async def notify_that_shift_is_finished(self, user: models.User, message: str) -> None:
        """Уведомляет участников об окончании смены."""
        text = message.format(name=user.name, surname=user.surname, numbers_lombaryers=user.numbers_lombaryers)
        await self.__bot.send_message(user.telegram_id, text)
