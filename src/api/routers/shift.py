from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.request_models.shift import ShiftCreateRequest
from src.api.response_models.shift import ShiftResponse
from src.core.services.shift_service import ShiftService

router = APIRouter(prefix="/shift", tags=["Shift"])


@router.post("/", response_model=ShiftResponse, response_model_exclude_none=True, status_code=HTTPStatus.CREATED)
async def create_new_shift(shift: ShiftCreateRequest, shift_service: ShiftService = Depends()) -> ShiftResponse:
    return await shift_service.create_new_shift(shift)


@router.get("/", response_model=ShiftResponse, response_model_exclude_none=True, status_code=HTTPStatus.OK)
async def get_shift(id: UUID, shift_service: ShiftService = Depends()) -> ShiftResponse:
    return await shift_service.get_shift(id)


@router.patch("/", response_model=ShiftResponse, response_model_exclude_none=True, status_code=HTTPStatus.OK)
async def update_shift(
    id: UUID, update_shift_data: ShiftCreateRequest, shift_service: ShiftService = Depends()
) -> ShiftResponse:
    return await shift_service.update_shift(id, update_shift_data)
