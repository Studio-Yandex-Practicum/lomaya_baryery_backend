from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.request_models.shift import ShiftCreateRequest
from src.core.db.db import get_session
from src.core.db.models import Shift


class ShiftService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_new_shift(
        self,
        new_shift: ShiftCreateRequest,
    ) -> Shift:
        db_shift = Shift(**new_shift.dict())
        self.session.add(db_shift)
        await self.session.commit()
        await self.session.refresh(db_shift)
        return db_shift


def get_shift_service(session: AsyncSession = Depends(get_session)) -> ShiftService:
    return ShiftService(session)
