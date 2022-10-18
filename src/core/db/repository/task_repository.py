from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Task, User
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

    async def get_tasks_report(self, user_id: UUID, task_id: UUID) -> dict:
        """Получить список задач с информацией о юзерах."""
        task_summary_info = await self.session.execute(
            select(
                User.name,
                User.surname,
                Task.id.label("task_id"),
                Task.description.label("task_description"),
                Task.url.label("task_url"),
            )
            .select_from(User, Task)
            .where(User.id == user_id, Task.id == task_id)
        )
        task_summary_info = task_summary_info.all()
        task = dict(*task_summary_info)
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
