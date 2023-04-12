from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Task
from src.core.db.repository import AbstractRepository


class TaskRepository(AbstractRepository):
    """Репозиторий для работы с моделью Task."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Task)

    async def get_task_ids_list(self) -> list[UUID]:
        """Список task_id неархивированных заданий."""
        task_ids = await self._session.execute(select(Task.id).where(Task.is_archived is False))
        return task_ids.scalars().all()
