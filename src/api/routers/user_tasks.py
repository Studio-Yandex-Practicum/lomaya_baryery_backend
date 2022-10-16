from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Path, FastAPI
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic.schema import UUID

from src.api.request_models.user_task import ChangeStatusRequest
from src.api.response_models.user_task import (
    UserTaskResponse,
    UserTasksAndShiftResponse,
)
from src.core.db.models import UserTask
from src.core.services.shift_service import ShiftService
from src.core.services.user_task_service import UserTaskService, get_user_task_service
from src.core.settings import settings

app = FastAPI()


router = APIRouter(prefix="/user_tasks", tags=["user_tasks"])


STR_ENTITY_NOT_EXIST = "Задачи с указанным id не существует!"
SHIFT_NOT_FOUND = "Такая смена не найдена, проверьте id."


@router.get(
    "/{user_task_id}",
    response_model=UserTaskResponse,
    response_model_exclude_none=True,
    summary="Получить информацию об отчёте участника.",
    response_description="Полная информация об отчёте участника.",
)
async def get_user_report(
    user_task_id: UUID,
    user_task_service: UserTaskService = Depends(get_user_task_service),
) -> UserTask:
    """Вернуть отчет участника.

    - **user_task_id**: номер задачи, назначенной участнику на день смены (генерируется рандомно при старте смены)
    - **task_id**: номер задачи
    - **day_number**: номер дня смены
    - **status**: статус задачи
    - **photo_url**: url фото выполненной задачи
    """
    user_task = await user_task_service.get_or_none(user_task_id)
    if user_task is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=STR_ENTITY_NOT_EXIST)
    return user_task


@router.patch(
    "/{user_task_id}",
    response_model=UserTaskResponse,
    response_model_exclude_none=True,
    summary="Изменить статус участника.",
    response_description="Полная информация об отчёте участника.",
)
async def change_user_report_status(
    user_task_id: UUID,
    request: ChangeStatusRequest,
    user_task_service: UserTaskService = Depends(get_user_task_service),
) -> UserTask:
    """Изменить статус отчета участника.

    - **user_task_id**: номер задачи, назначенной участнику на день смены (генерируется рандомно при старте смены)
    - **task_id**: номер задачи
    - **day_number**: номер дня смены
    - **status**: статус задачи
    - **photo_url**: url фото выполненной задачи
    """
    user_task = await user_task_service.get_or_none(user_task_id)
    if user_task is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=STR_ENTITY_NOT_EXIST)
    user_task = await user_task_service.change_status(user_task, request.status)
    return user_task


@router.get(
    "/{shift_id}/{day_number}/new",
    response_model=Page[UserTasksAndShiftResponse],
    summary="Получить непроверенные и новые задания.",
)
async def get_new_and_under_review_tasks(
    shift_id: UUID = Path(..., title="ID смены"),
    day_number: int = Path(..., title="Номер дня, от 1 до 93", ge=settings.MIN_DAYS, le=settings.MAX_DAYS),
    user_task_service: UserTaskService = Depends(get_user_task_service),
    shift_service: ShiftService = Depends(),
) -> dict[str, Union[dict, list]]:
    """Получить непроверенные и новые задания.

    Запрос информации о непроверенных и новых
    заданиях участников по состоянию на указанный день
    в определенной смене:

    - **shift_id**: уникальный id смены, ожидается в формате UUID.uuid4
    - **day_number**: номер дня смены, в диапазоне от 1 до 93
    """
    shift = await shift_service.get_shift(shift_id)
    if not shift:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=SHIFT_NOT_FOUND)
    tasks = await user_task_service.get_tasks_report(shift_id, day_number)
    report = dict()
    report["shift"] = shift
    report["tasks"] = tasks
    return paginate(report)

add_pagination(app)