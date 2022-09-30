from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Shift


class ShiftService:
    """Вспомогательный класс для Shift.

    Внутри реализован метод 'get' для получения
    экземпляра Shift.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_shift(self, shift_id: UUID) -> Shift:
        shift = await self.session.execute(select(Shift).where(Shift.id == shift_id))
        if not shift:
            raise HTTPException(status_code=404, detail="Такой смены не найдено.")
        return shift.scalars().first()


async def get_shift_service(session: AsyncSession = Depends(get_session)) -> ShiftService:
    return ShiftService(session)
