from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.api.request_models.shift import ShiftCreateRequest
from src.api.response_models.shift import ShiftResponse
from src.core.services.shift_service import ShiftService

router = APIRouter(prefix="/shifts", tags=["Shift"])


STR_STATUS_DENIES_START_SHIFT = "Нельзя запустить уже начатую, отмененную или завершенную смену."


@router.post(
    "/",
    response_model=ShiftResponse,
    response_model_exclude_none=True,
    status_code=HTTPStatus.CREATED,
    summary="Создать новую смену",
    response_description="Информация о созданной смене",
)
async def create_new_shift(shift: ShiftCreateRequest, shift_service: ShiftService = Depends()) -> ShiftResponse:
    """Создать новую смену.

    - **started_at**: дата начала смены
    - **finished_at**: дата окончания смены
    """
    return await shift_service.create_new_shift(shift)


@router.get(
    "/{shift_id}",
    response_model=ShiftResponse,
    response_model_exclude_none=True,
    status_code=HTTPStatus.OK,
    summary="Получить информацию о смене",
    response_description="Информация о смене",
)
async def get_shift(shift_id: UUID, shift_service: ShiftService = Depends()) -> ShiftResponse:
    """Получить информацию о смене по её ID.

    - **shift_id**: уникальный индентификатор смены
    - **status**: статус смены (started|finished|preparing|cancelled)
    - **started_at**: дата начала смены
    - **finished_at**: дата окончания смены
    """
    return await shift_service.get_shift(id)


@router.patch(
    "/{shift_id}",
    response_model=ShiftResponse,
    response_model_exclude_none=True,
    status_code=HTTPStatus.OK,
    summary="Обновить информацию о смене",
    response_description="Обновленная информация о смене",
)
async def update_shift(
    shift_id: UUID, update_shift_data: ShiftCreateRequest, shift_service: ShiftService = Depends()
) -> ShiftResponse:
    """Обновить информацию о смене с указанным ID.

    - **shift_id**: уникальный индентификатор смены
    - **started_at**: дата начала смены
    - **finished_at**: дата окончания смены
    """
    return await shift_service.update_shift(shift_id, update_shift_data)


@router.put(
    "/{shift_id}/actions/start",
    response_model=ShiftResponse,
    response_model_exclude_none=True,
    status_code=HTTPStatus.OK,
    summary="Старт смены",
    response_description="Информация о запущенной смене",
)
async def start_shift(shift_id: UUID, shift_service: ShiftService = Depends()) -> ShiftResponse:
    """Начать смену.

    - **shift_id**: уникальный индентификатор смены
    """
    try:
        shift = await shift_service.start_shift(shift_id)
    # TODO изменить на кастомное исключение
    except Exception:
        raise HTTPException(status_code=HTTPStatus.METHOD_NOT_ALLOWED, detail=STR_STATUS_DENIES_START_SHIFT)
    return shift
