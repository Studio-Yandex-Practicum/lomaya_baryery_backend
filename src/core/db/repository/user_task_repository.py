from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, false, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import UserTask
from src.core.db.repository import AbstractRepository


class UserTaskRepository(AbstractRepository):
    """Репозиторий для работы с моделью UserTask."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def get_or_none(self, id: UUID) -> Optional[UserTask]:
        return await self.session.get(UserTask, id)

    async def get(self, id: UUID) -> UserTask:
        user_task = await self.get_or_none(id)
        if user_task is None:
            # FIXME: написать и использовать кастомное исключение
            raise LookupError(f"Объект UserTask c {id=} не найден.")
        return user_task

    async def create(self, user_task: UserTask) -> UserTask:
        self.session.add(user_task)
        await self.session.commit()
        await self.session.refresh(user_task)
        return user_task

    async def update(self, id: UUID, user_task: UserTask) -> UserTask:
        user_task.id = id
        await self.session.merge(user_task)
        await self.session.commit()
        return user_task

    async def get_new_undeleted_by_user_id(self, user_id: UUID) -> Optional[UserTask]:
        """Получить наиболее раннюю задачу со статусом new и без признака удаления."""
        statement = select(UserTask).where(
            and_(UserTask.deleted == false(), UserTask.status == UserTask.Status.NEW.value, UserTask.user_id == user_id)
        ).order_by(UserTask.day_number)
        user_tasks = await self.session.execute(statement)
        return user_tasks.scalars().first()
