from src.bot.main import create_bot
from src.core import settings
from src.core.db import models
from src.core.db.repository import RequestRepository, UserRepository
from src.core.services.user_service import UserService

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


async def get_registration_service_callback(sessions):
    async for session in sessions:
        request_repository = RequestRepository(session)
        user_repository = UserRepository(session)
        registration_service = UserService(user_repository, request_repository)
        return registration_service
