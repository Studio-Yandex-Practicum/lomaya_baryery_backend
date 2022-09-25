from fastapi import APIRouter, Depends, HTTPException
from pydantic.schema import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.response_models.user_task import UserTaskDB
from src.core.db.db import get_session
from src.core.services.user_task_service import UserTaskService

router = APIRouter()


@router.get(
    "/{user_task_id}",
    response_model=UserTaskDB,
    response_model_exclude_none=True,
)
async def get_users_report(user_task_id: UUID, session: AsyncSession = Depends(get_session)):
    """Вернуть отчет участника."""
    user_task_service = UserTaskService(session=session)
    user_task = await user_task_service.get(user_task_id=user_task_id)
    if user_task is None:
        raise HTTPException(status_code=404, detail="Задачи с указанным id не существует!")
    return user_task
