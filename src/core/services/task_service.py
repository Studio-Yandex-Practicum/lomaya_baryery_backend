from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import Task


async def task_ids_list(
        session: AsyncSession,
) -> List:
    """Список всех task_id"""
    task_ids = await session.execute(
        select(
            Task.id
        )
    )
    return task_ids.scalars().all()
