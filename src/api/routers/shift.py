from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.request_models.shift import ShiftCreateRequest
from src.api.response_models.shift import ShiftResponse
from src.core.services.shift_service import ShiftService
from src.core.services.user_task_service import UserTaskService

router = APIRouter(prefix="/shifts", tags=["Shift"])


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
    "/",
    response_model=ShiftResponse,
    response_model_exclude_none=True,
    status_code=HTTPStatus.OK,
    summary="Получить информацию о смене",
    response_description="Информация о смене",
)
async def get_shift(id: UUID, shift_service: ShiftService = Depends()) -> ShiftResponse:
    """Получить информацию о смене по её ID.

    - **id**: уникальный индентификатор смены
    - **status**: статус смены (started|finished|preparing|cancelled)
    - **started_at**: дата начала смены
    - **finished_at**: дата окончания смены
    """
    return await shift_service.get_shift(id)


@router.patch(
    "/",
    response_model=ShiftResponse,
    response_model_exclude_none=True,
    status_code=HTTPStatus.OK,
    summary="Обновить информацию о смене",
    response_description="Обновленная информация о смене",
)
async def update_shift(
    id: UUID, update_shift_data: ShiftCreateRequest, shift_service: ShiftService = Depends()
) -> ShiftResponse:
    """Обновить информацию о смене с указанным ID.

    - **started_at**: дата начала смены
    - **finished_at**: дата окончания смены
    """
    return await shift_service.update_shift(id, update_shift_data)


@router.post(
    "/{shift_id}",
    response_model=ShiftResponse,
    response_model_exclude_none=True,
    status_code=HTTPStatus.OK,
    summary="Старт смены",
    response_description="Информация о запущенной смене",
)
async def start_shift(
    shift_id: UUID,
    shift_service: ShiftService = Depends(),
) -> ShiftResponse:
    """Запустить смену.

    - **shift_id**: уникальный индентификатор смены
    """
    user_service = UserTaskService(shift_service.shift_repository.session)
    user_service.distribute_tasks_on_shift(shift_id)
    # TODO добавить вызов метода рассылки участникам первого задания
    return await shift_service.start_shift(shift_id)
