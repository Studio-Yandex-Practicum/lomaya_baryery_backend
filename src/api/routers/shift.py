from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.request_models.shift import ShiftCreate
from src.api.response_models.shift import ShiftDB
from src.core.db.db import get_session
from src.core.services.shift_service import ShiftService, get_shift_service

router = APIRouter()


@router.post("/shift/create", response_model=ShiftDB, response_model_exclude_none=True)
async def create_new_shift(
    shift: ShiftCreate,
    shift_service: ShiftService = Depends(get_shift_service),
    session: AsyncSession = Depends(get_session),
):
    return await shift_service(session).create_new_shift(new_shift=shift)
