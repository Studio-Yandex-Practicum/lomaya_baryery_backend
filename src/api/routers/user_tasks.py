from fastapi import APIRouter, HTTPException
from pydantic.schema import UUID

from src.api.response_models.user_task import UserTaskDB
from src.core.services.user_task_service import UserTaskService

router = APIRouter()


@router.get(
    "/{user_task_id}",
    response_model=UserTaskDB,
    response_model_exclude_none=True,
)
async def get_users_report(user_task_id: UUID):
    """Вернуть отчет участника."""
    user_task = await UserTaskService.get(user_task_id=user_task_id)
    if user_task is None:
        raise HTTPException(status_code=404, detail="Задачи с указанным id не существует!")
    return user_task
