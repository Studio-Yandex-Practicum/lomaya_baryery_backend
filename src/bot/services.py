from src.core import settings
from src.core.db import models
# from src.bot.main import create_bot
from src.schemas.user import UserData
from src.schemas.registration import RequestData
from src.core.db.db import async_session
from src.core.crud.user import user_crud
from src.core.crud.request import request_crud


# bot = create_bot().bot  # временная копия бота до миграции на webhooks


async def send_approval_callback(user: models.User):
    await bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f'Привет, {user.name} {user.surname}! Поздравляем, ты в проекте!'
        )
    )


async def send_rejection_callback(user: models.User):
    await bot.send_message(
        chat_id=user.telegram_id,
        text=(
            f'К сожалению, на данный момент мы не можем зарегистрировать вас'
            f' в проекте. Вы можете написать на почту '
            f'{settings.ORGANIZATIONS_EMAIL}. Чтобы не пропустить актуальные'
            f' новости Центра "Ломая барьеры" - вступайте в нашу группу '
            f'{settings.ORGANIZATIONS_GROUP}'
        )
    )


async def is_user_valid_for_registration(telegram_id) -> bool:
    """Проверка пользователя на доступ к регистрации."""
    return True


async def registration(user_data):
    """Регистрация пользователя."""
    async with async_session() as session:
        telegram_id = user_data.get('telegram_id')
        user = await user_crud.get_by_attribute(attr_name='telegram_id',
                                                attr_value=telegram_id,
                                                session=session)
        if not user:
            user_obj = UserData(**user_data)
            user = await user_crud.create(obj_in=user_obj,
                                          session=session)
        request_obj = RequestData(user_id=user.id)
        await request_crud.create(obj_in=request_obj,
                                  session=session)
