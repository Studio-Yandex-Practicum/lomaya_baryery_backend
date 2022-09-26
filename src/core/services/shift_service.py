from sqlalchemy.ext.asyncio import AsyncSession

from src.api.request_models.shift import ShiftCreate
from src.core.db.models import Shift


class ShiftService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_new_shift(
        self,
        new_shift: ShiftCreate,
    ) -> Shift:
        new_shift_data = new_shift.dict()
        db_shift = Shift(**new_shift_data)
        self.session.add(db_shift)
        await self.session.commit()
        await self.session.refresh(db_shift)
        return db_shift


def get_shift_service() -> ShiftService:
    return ShiftService
