from src.api.request_models.request import Status
from src.bot.main import create_bot
from src.core import settings
from src.core.db import models

bot = create_bot().bot  # временная копия бота до миграции на webhooks


async def send_approval_callback(user: models.User):
    await bot.send_message(
        chat_id=user.telegram_id, text=(f"Привет, {user.name} {user.surname}! Поздравляем, ты в проекте!")
    )


async def send_rejection_callback(user: models.User):
    await bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"К сожалению, на данный момент мы не можем зарегистрировать вас"
            f" в проекте. Вы можете написать на почту "
            f"{settings.ORGANIZATIONS_EMAIL}. Чтобы не пропустить актуальные"
            f" новости Центра \"Ломая барьеры\" - вступайте в нашу группу "
            f"{settings.ORGANIZATIONS_GROUP}"
        ),
    )


async def send_change_task_status_notifitation_callback(user_task: models.UserTask, telegram_id: int):
    """Уведомление о проверенном задании."""
    if user_task.status is Status.APPROVED:
        text_reply = f"""
        Твой отчет от {user_task.photo.updated_at} принят!
        Тебе начислен 1 \"ломбарьерчик\".
        Следующее задание придет в 8.00 мск.
        """
    else:
        text_reply = """
            К сожалению, мы не можем принять твой фотоотчет!
            Возможно на фотографии не видно, что именно ты выполняешь задание.
            Предлагаем продолжить, ведь впереди много интересных заданий.
            Следующее задание придет в 8.00 мск.
        """
    await bot.send_message(chat_id=telegram_id, text=text_reply)
