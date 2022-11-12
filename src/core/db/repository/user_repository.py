from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Shift, User
from src.core.db.repository import AbstractRepository


class UserRepository(AbstractRepository):
    """Репозиторий для работы с моделью User."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def get_or_none(self, id: UUID) -> Optional[User]:
        return await self.session.get(User, id)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        user = await self.session.execute(select(User).where(telegram_id == telegram_id))
        return user.scalars().first()

    async def check_user_existence(self, telegram_id: int, phone_number: str) -> bool:
        user_exists = await self.session.execute(
            exists().where(or_(User.phone_number == phone_number, User.telegram_id == telegram_id))
        )
        return user_exists.scalar()

    async def get_users_in_active_shift(self) -> list[User]:
        user_in_active_shift = await self.session.execute(
            select(User).where(Shift.status == Shift.Status.STARTED.value).join(User.shifts)
        )
        users_in_active_shift = user_in_active_shift.scalars().all()
        return users_in_active_shift

    async def get(self, id: UUID) -> User:
        user = await self.get_or_none(id)
        if user is None:
            # FIXME: написать и использовать кастомное исключение
            raise LookupError(f"Объект User c {id=} не найден.")
        return user

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, id: UUID, user: User) -> User:
        user.id = id
        await self.session.merge(user)
        await self.session.commit()
        return user
