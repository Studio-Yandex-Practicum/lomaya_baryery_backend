from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import Request


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
            Request.status == Request.Status.APPROVED.title()
        )
    )
    return user_ids.scalars().all()
