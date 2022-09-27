from fastapi import Depends
from pydantic.schema import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Request


class RequestService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_ids_approved_to_shift(
        self,
        shift_id: UUID,
    ) -> list[UUID]:
        """Список id пользователей одобренных на смену shift_id."""
        user_ids = await self.session.execute(
            select(Request.user_id)
            .where(Request.shift_id == shift_id)
            .where(Request.status == Request.Status.APPROVED.title())
        )
        return user_ids.scalars().all()


async def get_request_service(session: AsyncSession = Depends(get_session)) -> RequestService:
    return RequestService(session)
