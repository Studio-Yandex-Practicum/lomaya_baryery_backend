from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import Request, Task


async def user_ids_approved_to_shift(
        shift_id: int,
        session: AsyncSession
) -> List:
    """Список id пользователей одобренных на смену shift_id."""
    user_ids = await session.execute(
        select(
            Request.user_id
        ).where(
            Request.shift_id == shift_id
        ).where(
            Request.status == "approved"
        )
    )
    return user_ids.scalars().all()


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
