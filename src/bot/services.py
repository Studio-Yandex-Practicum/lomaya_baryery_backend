from telegram import ReplyKeyboardMarkup

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


async def send_task_callback(user: models.User, description: str, task_url: str):
    buttons = ReplyKeyboardMarkup([["Пропустить задание", "Баланс ломбарьеров"]], resize_keyboard=True)
    await bot.send_message(chat_id=user.telegram_id, text=(task_url))
    await bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f"Сегодня твоим заданием будет {description}."
            f"Не забудь сделать фотографию, как ты выполняешь задание и отправить на проверку."
        ),
        reply_markup=buttons,
    )
