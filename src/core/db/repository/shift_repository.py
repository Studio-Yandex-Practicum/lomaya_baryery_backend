from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Shift, User
from src.core.db.repository import AbstractRepository


class ShiftRepository(AbstractRepository):
    """Репозиторий для работы с моделью Shift."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def get_or_none(self, id: UUID) -> Optional[Shift]:
        return await self.session.get(Shift, id)

    async def get(self, id: UUID) -> Shift:
        shift = await self.get_or_none(id)
        if shift is None:
            # FIXME: написать и использовать кастомное исключение
            raise LookupError(f"Объект Shift c {id=} не найден.")
        return shift

    async def create(self, shift: Shift) -> Shift:
        self.session.add(shift)
        await self.session.commit()
        await self.session.refresh(shift)
        return shift

    async def update(self, id: UUID, shift: Shift) -> Shift:
        shift.id = id
        shift = await self.session.merge(shift)
        await self.session.commit()
        return shift

    async def get_users(self, id: UUID) -> list[User]:
        pass
