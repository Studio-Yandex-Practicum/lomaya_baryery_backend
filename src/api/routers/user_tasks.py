from http import HTTPStatus

from fastapi import APIRouter, Depends
from pydantic.schema import UUID

from src.api.request_models.user_task import ChangeStatusRequest
from src.api.response_models.user_task import UserTaskResponse
from src.core.db.models import UserTask
from src.core.services.user_task_service import UserTaskService

router = APIRouter(prefix="/user_tasks", tags=["UserTask"])


@router.get(
    "/{user_task_id}",
    response_model=UserTaskResponse,
    response_model_exclude_none=True,
    summary="Получить информацию об отчёте участника.",
    response_description="Полная информация об отчёте участника.",
)
async def get_user_report(
    id: UUID,
    user_task_service: UserTaskService = Depends(),
):
    """Вернуть отчет участника.

    - **user_task_id**: номер задачи, назначенной участнику на день смены (генерируется рандомно при старте смены)
    - **task_id**: номер задачи
    - **day_number**: номер дня смены
    - **status**: статус задачи
    - **photo_url**: url фото выполненной задачи
    """
    user_task = await user_task_service.get_user_task_photo(id)
    return user_task


@router.patch(
    "/{user_task_id}",
    response_model=UserTaskResponse,
    response_model_exclude_none=True,
    status_code=HTTPStatus.OK,
    summary="Изменить статус участника.",
    response_description="Полная информация об отчёте участника.",
)
async def update_status(
    user_task_id: UUID,
    update_user_task_status: ChangeStatusRequest,
    user_task_service: UserTaskService = Depends(),
) -> UserTask:
    """Изменить статус отчета участника.

    - **user_task_id**: номер задачи, назначенной участнику на день смены (генерируется рандомно при старте смены)
    - **task_id**: номер задачи
    - **day_number**: номер дня смены
    - **status**: статус задачи
    - **photo_url**: url фото выполненной задачи
    """
    user_task = await user_task_service.get_user_task_photo(user_task_id)
    user_task = await user_task_service.update_status(id=user_task.id, update_user_task_status=update_user_task_status)
    return user_task
