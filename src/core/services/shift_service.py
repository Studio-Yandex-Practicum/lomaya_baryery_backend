from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import Shift


async def get_shift(shift_id: UUID, session: AsyncSession) -> Shift:
    """Получаем данные смены.

    Используется для ЭПИКА 'API: список заданий на проверке'.
    """
    shift = await session.execute(select(Shift).where(Shift.id == shift_id))
    if not shift:
        raise HTTPException(status_code=404, detail="Такой смены не найдено.")
    return shift.scalars().first()
