import os

from telegram import Update
from telegram.ext import CallbackContext

from src.core import settings
from src.core.db import models
from src.core.settings import BASE_DIR
from src.bot.main import create_bot

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


async def download_photo_report_callback(update: Update, context: CallbackContext) -> str:
    """Сохранить фото отчёта на диск в /data/user_reports."""
    USER_REPORTS_DIR = os.path.join(BASE_DIR, settings.settings.DATA_DIR, settings.settings.USER_REPORTS_DIR)

    if not os.path.exists(USER_REPORTS_DIR):
        os.makedirs(USER_REPORTS_DIR)
    file = await context.bot.get_file(update.message.photo[-1].file_id)
    _, ext = os.path.splitext(file.file_path)
    file_name = file.file_unique_id.replace('-', '') + ext
    await file.download(custom_path=os.path.join(USER_REPORTS_DIR, file_name))
    return str(file.file_path)
