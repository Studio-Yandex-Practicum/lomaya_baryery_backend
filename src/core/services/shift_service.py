from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import Shift
from src.api.request_models.shift import ShiftCreate


class ShiftService:
    def __init__(self, session: AsyncSession) -> AsyncSession:
        self.session = session

    async def create_new_shift(
        new_shift: ShiftCreate,
        session,
    ) -> Shift:
        new_shift_data = new_shift.dict()
        db_shift = Shift(**new_shift_data)
        session.add(db_shift)
        await session.commit()
        await session.refresh(db_shift)
        return db_shift
