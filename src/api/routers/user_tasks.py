from fastapi import APIRouter, Depends, HTTPException
from pydantic.schema import UUID

from src.api.response_models.user_task import UserTaskDB
from src.core.services.user_task_service import UserTaskService, get_user_task_service

router = APIRouter()


@router.get(
    "/user/task/{user_task_id}",
    response_model=UserTaskDB,
    response_model_exclude_none=True,
)
async def get_users_report(user_task_id: UUID, user_task_service: UserTaskService = Depends(get_user_task_service)):
    """Вернуть отчет участника."""
    user_task = await user_task_service.get(user_task_id=user_task_id)
    if user_task is None:
        raise HTTPException(status_code=404, detail="Задачи с указанным id не существует!")
    return user_task
