from typing import Optional

from fastapi import Depends
from sqlalchemy import exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Shift, User
from src.core.db.repository import AbstractRepository


class UserRepository(AbstractRepository):
    """Репозиторий для работы с моделью User."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        AbstractRepository.__init__(self, session, model=User)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        user = await self._session.execute(select(User).where(telegram_id == telegram_id))
        return user.scalars().first()

    async def check_user_existence(self, telegram_id: int, phone_number: str) -> bool:
        user_exists = await self._session.execute(
            exists().where(or_(User.phone_number == phone_number, User.telegram_id == telegram_id))
        )
        return user_exists.scalar()

    async def get_users_in_active_shift(self) -> list[User]:
        user_in_active_shift = await self._session.execute(
            select(User).where(Shift.status == Shift.Status.STARTED.value).join(User.shifts)
        )
        users_in_active_shift = user_in_active_shift.scalars().all()
        return users_in_active_shift
