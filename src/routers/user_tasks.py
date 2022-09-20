from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pydantic.schema import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Photo, UserTask, UserTaskStatuses

router = APIRouter()


class UserTaskDB(BaseModel):
    """Pydantic-схема, для описания объекта, полученного из БД"""
    user_task_id: UUID
    task_id: UUID
    day_number: int
    status: UserTaskStatuses
    photo_url: str

    class Config:
        orm_mode = True


async def get(
        user_task_id: UUID,
        session: AsyncSession,
):
    """Получить объект отчета участника по id."""
    user_task = await session.execute(
        select(UserTask, Photo.url.label('photo_url')).where(
            UserTask.id == user_task_id
        )
    )
    return user_task.scalars().first()


async def check_user_task_exists(
        user_task_id: UUID,
        session: AsyncSession,
) -> UserTask:
    """Проверить наличие отчета участника в БД по id."""
    user_task = await get(
        user_task_id=user_task_id,
        session=session
    )
    if user_task is None:
        raise HTTPException(
            status_code=404,
            detail='Задачи с указанным id не существует!'
        )
    return user_task


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
