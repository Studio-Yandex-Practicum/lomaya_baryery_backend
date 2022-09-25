from pydantic.schema import UUID
from sqlalchemy import select

from src.core.db.models import Photo, UserTask


class UserTaskService:
    def __init__(self, session):
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
