from datetime import date
from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, Depends, Path
from pydantic.schema import UUID

from src.api.request_models.user_task import ChangeStatusRequest
from src.api.response_models.user_task import (
    UserTaskResponse,
    UserTasksAndShiftResponse,
)
from src.core.services.shift_service import ShiftService
from src.core.services.user_task_service import UserTaskService
from src.core.settings import settings

router = APIRouter(prefix="/user_tasks", tags=["user_tasks"])


@router.get(
    "/{user_task_id}",
    response_model=UserTaskResponse,
    response_model_exclude_none=True,
    status_code=HTTPStatus.OK,
    summary="Получить информацию об отчёте участника.",
    response_description="Полная информация об отчёте участника.",
)
async def get_user_report(
    user_task_id: UUID,
    user_task_service: UserTaskService = Depends(),
) -> dict:
    """Вернуть отчет участника.

    - **user_id**:номер участника
    - **user_task_id**: номер задачи, назначенной участнику на день смены (генерируется рандомно при старте смены)
    - **task_id**: номер задачи
    - **day**: дата получения задания
    - **status**: статус задачи
    - **photo_url**: url фото выполненной задачи
    """
    user_task = await user_task_service.get_user_task_with_photo_url(user_task_id)
    return user_task


@router.patch(
    "/{user_task_id}",
    response_model=UserTaskResponse,
    response_model_exclude_none=True,
    status_code=HTTPStatus.OK,
    summary="Изменить статус участника.",
    response_description="Полная информация об отчёте участника.",
)
async def update_status_report(
    user_task_id: UUID,
    update_user_task_status: ChangeStatusRequest,
    user_task_service: UserTaskService = Depends(),
) -> dict:
    """Изменить статус отчета участника.

    - **user_id**:номер участника
    - **user_task_id**: номер задачи, назначенной участнику на день смены (генерируется рандомно при старте смены)
    - **task_id**: номер задачи
    - **day**: дата получения задания
    - **status**: статус задачи
    - **photo_url**: url фото выполненной задачи
    """
    user_task = await user_task_service.update_status(user_task_id, update_user_task_status)
    return user_task


@router.get(
    "/{shift_id}/{day}/new",
    response_model=UserTasksAndShiftResponse,
    summary="Получить непроверенные и новые задания.",
)
async def get_new_and_under_review_tasks(
    shift_id: UUID = Path(..., title="ID смены"),
    day: date = Path(..., title="Дата получения задания"),
    user_task_service: UserTaskService = Depends(),
    shift_service: ShiftService = Depends(),
) -> dict[str, Union[dict, list]]:
    """Получить непроверенные и новые задания.

    Запрос информации о непроверенных и новых
    заданиях участников по состоянию на указанный день
    в определенной смене:

    - **shift_id**: уникальный id смены, ожидается в формате UUID.uuid4
    - **day**: дата получения задания, ожидается в формате yyyy-mm-dd
    """
    shift = await shift_service.get_shift(shift_id)
    tasks = await user_task_service.get_tasks_report(shift_id, day)
    report = dict()
    report["shift"] = shift
    report["tasks"] = tasks
    return report
