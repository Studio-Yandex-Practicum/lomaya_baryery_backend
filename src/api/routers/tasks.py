from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.services.shift_service import create_new_shift
from src.api.request_models.shift import ShiftCreate
from src.api.response_models.shift import ShiftDB

router = APIRouter()


@router.post(
    '/',
    response_model=ShiftDB,
)
async def create_new_task(
    shift: ShiftCreate,
    session: AsyncSession = Depends(get_session)
):
    """Только для суперюзеров."""
    new_room = await create_new_shift(shift, session)
    return new_room
