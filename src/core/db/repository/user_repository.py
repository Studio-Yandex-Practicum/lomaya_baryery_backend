from typing import Optional

from fastapi import Depends
from sqlalchemy import exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import User
from src.core.db.repository import AbstractRepository


class UserRepository(AbstractRepository):
    """Репозиторий для работы с моделью User."""

    _model = User

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self._session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        user = await self._session.execute(select(User).where(telegram_id == telegram_id))
        return user.scalars().first()

    async def check_user_existence(self, telegram_id: int, phone_number: str) -> bool:
        user_exists = await self._session.execute(
            exists().where(or_(User.phone_number == phone_number, User.telegram_id == telegram_id))
        )
        return user_exists.scalar()
