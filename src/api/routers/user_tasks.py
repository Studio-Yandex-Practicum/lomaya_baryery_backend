from fastapi import APIRouter, Depends

from pydantic.schema import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.response_models.user_task import UserTaskDB
from src.api.routers.services import check_user_task_exists
from src.core.db.db import get_session


router = APIRouter()


@router.get(
    '/{user_task_id}',
    response_model=UserTaskDB,
    response_model_exclude_none=True,
)
async def get_users_report(
        user_task_id: UUID,
        session: AsyncSession = Depends(get_session)
):
    """Вернуть отчет участника."""
    user_task = await check_user_task_exists(user_task_id, session)
    return user_task
