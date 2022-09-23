from enum import Enum
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pydantic.schema import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Photo, UserTask

router = APIRouter()


class StatusEnum(str, Enum):
    """Допустимые статусы."""

    APPROVED = 'approved'
    DECLINED = 'declined'


class UserTaskDB(BaseModel):
    """Схема выходных данных."""

    user_task_id: UUID
    task_id: UUID
    day_number: int
    status: StatusEnum
    photo_url: str

    class Config:
        orm_mode = True


async def db_get(
        obj_id,
        session: AsyncSession,
) -> Optional[UserTask]:
    """Получение объекта базы."""
    user_task = await session.execute(
        select(UserTask, Photo.url.label('photo_url')).where(
            UserTask.id == obj_id
        )
    )
    return user_task.scalars().first()


async def db_update_status(
        db_obj,
        status,
        session: AsyncSession,
) -> UserTask:
    """Обновление статуса объекта."""
    db_obj.status = status
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj


async def check_user_task_exist(
        user_task_id: UUID,
        session: AsyncSession,
) -> UserTask:
    """Существует ли задание."""
    user_task = await db_get(user_task_id, session)
    if user_task is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Задание не найдено',
        )
    return user_task


@router.patch(
    '/{user_task_id}/{status}',
    response_model=UserTaskDB,
    response_model_exclude_none=True,
    # указать пермишн только для администратора
)
async def change_user_task_status(
        user_task_id: UUID,
        status: StatusEnum,
        session: AsyncSession = Depends(get_session),
):
    """Изменение статуса задания."""
    user_task = await check_user_task_exist(user_task_id, session)
    user_task = await db_update_status(user_task, status, session)
    return user_task
