from fastapi import Depends
from telegram import Bot

from src.bot.main import create_bot
from src.core import settings
from src.core.db import models


class BotService:
    def __init__(self, bot: Bot = Depends(create_bot)) -> None:
        self.bot = bot

    async def notify_approved_request(self, user: models.User) -> None:
        """Уведомление участника о решении по заявке в telegram.

        - Заявка принята.
        """
        text = f"Привет, {user.name} {user.surname}! Поздравляем, ты в проекте!"
        await self.bot.send_message(user.telegram_id, text)

    async def notify_declined_request(self, user: models.User) -> None:
        """Уведомление участника о решении по заявке в telegram.

        - Заявка отклонена.
        """
        text = (
            f"К сожалению, на данный момент мы не можем зарегистрировать вас"
            f" в проекте. Вы можете написать на почту "
            f"{settings.ORGANIZATIONS_EMAIL}. Чтобы не пропустить актуальные"
            f" новости Центра \"Ломая барьеры\" - вступайте в нашу группу "
            f"{settings.ORGANIZATIONS_GROUP}"
        )
        await self.bot.send_message(user.telegram_id, text)

    async def notify_approved_task(self, user_task: models.UserTask) -> None:
        """Уведомление участника о проверенном задании.

        - Задание принято, начислен 1 ломбарьерчик.
        """
        text = (
            f"Твой отчет от {user_task.photo.created_at} принят! "
            f"Тебе начислен 1 \"ломбарьерчик\". "
            f"Следуюее задание придет в 8.00 мск."
        )
        await self.bot.send_message(user_task.user.telegram_id, text)

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
        await self.bot.send_message(telegram_id, text)
