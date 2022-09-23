from fastapi import HTTPException
from pydantic.schema import UUID
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.db.models import Photo, UserTask


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
