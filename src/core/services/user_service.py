from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import User


async def get_user_info(user_id: UUID, session: AsyncSession) -> dict[str, str]:
    """Получаем имя и фамилию юзера.

    Используется для ЭПИКА 'API: список заданий на проверке'.
    """
    user_info = await session.execute(select([User.name, User.surname]).where(User.id == user_id))
    user_info = user_info.all()
    user_info = dict(user_info[0])
    return user_info
