from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.services.shift_service import ShiftService
from src.api.request_models.shift import ShiftCreate
from src.api.response_models.shift import ShiftDB


router = APIRouter()


@router.post(
    '/shift/create',
    response_model=ShiftDB,
    response_model_exclude_none=True
)
async def create_new_shift(
    shift: ShiftCreate,
    session: AsyncSession = Depends(get_session)
):
    """Только для суперюзеров."""
    new_shift = await ShiftService.create_new_shift(shift, session)
    return new_shift
