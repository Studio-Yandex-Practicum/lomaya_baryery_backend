from src.api.request_models.request import Status
from src.bot.main import create_bot
from src.core import settings
from src.core.db import models

bot = create_bot().bot  # временная копия бота до миграции на webhooks


async def send_message_about_new_request_status(user: models.User, status: str) -> None:
    """Отправить сообщение о решении по заявке в telegram."""
    text = f"Привет, {user.name} {user.surname}! Поздравляем, ты в проекте!"
    if status is Status.DECLINED:
        text = (
            f"К сожалению, на данный момент мы не можем зарегистрировать вас"
            f" в проекте. Вы можете написать на почту "
            f"{settings.ORGANIZATIONS_EMAIL}. Чтобы не пропустить актуальные"
            f" новости Центра \"Ломая барьеры\" - вступайте в нашу группу "
            f"{settings.ORGANIZATIONS_GROUP}"
        )
        await bot.send_message(chat_id=user.telegram_id, text=text)


async def send_message_about_change_task_status(user_task: str, telegram_id: str, photo_created_at: str):
    """Уведомление о проверенном задании."""
    text = f"""Твой отчет от {photo_created_at} принят!
        Тебе начислен 1 \"ломбарьерчик\".
        Следующее задание придет в 8.00 мск.
        """
    if user_task.status is Status.DECLINED:
        text = """
            К сожалению, мы не можем принять твой фотоотчет!
            Возможно на фотографии не видно, что именно ты выполняешь задание.
            Предлагаем продолжить, ведь впереди много интересных заданий.
            Следующее задание придет в 8.00 мск.
        """
    await bot.send_message(chat_id=telegram_id, text=text)
