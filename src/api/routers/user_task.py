from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.response_models.user_task import UserTaskResponseModel
from src.core.db.db import get_session
from src.core.db.models import UserTask
from src.core.services.user_task_service import UserTaskService
from src.core.settings import settings

router = APIRouter()


@router.get(
    "/user/task/{shift_id}/{day_number}/new",
    response_model=UserTaskResponseModel,
    summary="Получить непроверенные и новые задания",
)
async def get_new_and_under_review_tasks(
    shift_id: UUID = Path(..., title="ID смены"),
    day_number: int = Path(..., title="Номер дня, от 1 до 93", ge=settings.MIN_DAYS, le=settings.MAX_DAYS),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Union[dict, list]]:
    """Получить непроверенные и новые задания.

    Запрос информации о непроверенных и новых
    заданиях участников по состоянию на указанный день
    в определенной смене:

    - **shift_id**: никальный id смены, ожидается в формате UUID.uuid4
    - **day_number**: номер дня смены, в диапазоне от 1 до 93
    """
    user_task_manager = UserTaskService(shift_id, day_number, UserTask)
    response = await user_task_manager.get_report(session)
    return response
