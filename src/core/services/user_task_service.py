from pydantic.schema import UUID
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.db.models import Photo, UserTask


class UserTaskService:
    async def get(
        self,
        user_task_id: UUID,
        session: AsyncSession,
    ):
        """Получить объект отчета участника по id."""
        user_task = await session.execute(
            select(UserTask, Photo.url.label("photo_url")).where(UserTask.id == user_task_id)
        )
        return user_task.scalars().first()
