from typing import List

from fastapi import Depends
from pydantic.schema import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Task


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_task_ids_list(
        self,
    ) -> List[UUID]:
        """Список всех task_id."""
        task_ids = await self.session.execute(select(Task.id))
        return task_ids.scalars().all()


async def get_task_service(session: AsyncSession = Depends(get_session)) -> TaskService:
    return TaskService(session)
