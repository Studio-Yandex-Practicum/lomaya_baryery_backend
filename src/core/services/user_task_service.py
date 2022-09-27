from fastapi import Depends
from pydantic.schema import UUID
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Photo, UserTask


class UserTaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(
        self,
        user_task_id: UUID,
    ):
        """Получить объект отчета участника по id."""
        user_task = await self.session.execute(
            select(UserTask, Photo.url.label("photo_url")).where(UserTask.id == user_task_id)
        )
        return user_task.scalars().first()


async def get_user_task_service(session: AsyncSession = Depends(get_session)) -> UserTaskService:
    user_task_service = UserTaskService(session)
    return user_task_service
