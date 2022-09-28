from pydantic.schema import UUID
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.request_models.user_task import AllowedUserTaskStatus
from src.core.db.models import Photo, UserTask


class UserTaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(
        self,
        user_task_id: UUID,
    ) -> UserTask:
        """Получить объект отчета участника по id."""
        user_task = await self.session.execute(
            select(UserTask, Photo.url.label("photo_url")).where(UserTask.id == user_task_id)
        )
        return user_task.scalars().first()

    async def change_status(
        self,
        user_task: UserTask,
        status: AllowedUserTaskStatus,
    ) -> UserTask:
        """Изменить статус задачи."""
        user_task.status = status
        self.session.add(user_task)
        await self.session.commit()
        await self.session.refresh(user_task)
        return user_task
