from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Task
from src.core.db.repository import AbstractRepository


class TaskRepository(AbstractRepository):
    """Репозиторий для работы с моделью Task."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def get_or_none(self, id: UUID) -> Optional[Task]:
        return await self.session.get(Task, id)

    async def get(self, id: UUID) -> Task:
        task = await self.get_or_none(id)
        if task is None:
            # FIXME: написать и использовать кастомное исключение
            raise LookupError(f"Объект Task c {id=} не найден.")
        return task

    async def create(self, task: Task) -> Task:
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def update(self, id: UUID, task: Task) -> Task:
        task.id = id
        await self.session.merge(task)
        await self.session.commit()
        return task
