from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Task, User
from src.core.db.repository import AbstractRepository

from .abstract_repository import DatabaseModel


class TaskRepository(AbstractRepository):
    """Репозиторий для работы с моделью Task."""

    def __init__(self, session: AsyncSession = Depends(get_session), model: DatabaseModel = Task) -> None:
        self._session = session
        self._model = model

    async def get_task_ids_list(self) -> list[UUID]:
        """Список всех task_id."""
        task_ids = await self._session.execute(select(Task.id))
        return task_ids.scalars().all()

    async def get_tasks_report(self, user_id: UUID, task_id: UUID) -> dict:
        """Получить список задач с информацией о юзерах."""
        task_summary_info = await self._session.execute(
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
