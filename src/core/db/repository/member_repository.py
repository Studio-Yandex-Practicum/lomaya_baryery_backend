from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.db.db import get_session
from src.core.db.models import Member, User
from src.core.db.repository import AbstractRepository
from src.core.exceptions import NotFoundException


class MemberRepository(AbstractRepository):
    """Репозиторий для работы с моделью Member."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Member)

    async def get_by_user_and_shift(self, shift_id: UUID, user_id: UUID) -> Member:
        member = await self._session.execute(
            select(Member).where(Member.shift_id == shift_id, Member.user_id == user_id)
        )
        return member.scalars().first()

    async def get_with_user_info(self, id: UUID) -> Member:
        member = await self._session.execute(select(Member).where(Member.id == id).options(selectinload(User)))
        if not member:
            raise NotFoundException
        return member.scalars().first()
