from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic.schema import UUID

from src.api.request_models.user_task import AllowedUserTaskStatus
from src.api.response_models.user_task import UserTaskDB
from src.core.services.user_task_service import UserTaskService, get_user_task_service

router = APIRouter()


@router.get(
    "/user/task/{user_task_id}",
    response_model=UserTaskDB,
    response_model_exclude_none=True,
    summary="Получить информацию об отчёте участника.",
    response_description="Полная информация об отчёте участника.",
)
async def get_users_report(user_task_id: UUID, user_task_service: UserTaskService = Depends(get_user_task_service)):
    """Вернуть отчет участника.

    - **user_task_id**: номер задачи, назначенной участнику на день смены (генерируется рандомно при старте смены)
    - **task_id**: номер задачи
    - **day_number**: номер дня смены
    - **status**: статус задачи
    - **photo_url**: url фото выполненной задачи
    """
    user_task = await user_task_service.get(user_task_id=user_task_id)
    if user_task is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Задачи с указанным id не существует!")
    return user_task


@router.patch(
    "/user/task/{user_task_id}/{status}",
    response_model=UserTaskDB,
    response_model_exclude_none=True,
    summary="Изменить статус участника.",
    response_description="Полная информация об отчёте участника.",
)
async def change_users_report_status(
    user_task_id: UUID,
    status: AllowedUserTaskStatus,
    user_task_service: UserTaskService = Depends(get_user_task_service),
):
    """Изменить статус отчета участника.

    - **user_task_id**: номер задачи, назначенной участнику на день смены (генерируется рандомно при старте смены)
    - **task_id**: номер задачи
    - **day_number**: номер дня смены
    - **status**: статус задачи
    - **photo_url**: url фото выполненной задачи
    """
    user_task = await get_users_report(user_task_id)
    await user_task_service.change_task_status(user_task=user_task, status=status)
    return user_task
