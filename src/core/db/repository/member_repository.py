from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Member
from src.core.db.repository import AbstractRepository


class MemberRepository(AbstractRepository):
    """Репозиторий для работы с моделью Member."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Member)

    async def get_by_user_and_shift(self, user_id: UUID, shift_id: UUID) -> Member:
        member = await self._session.execute(
            select(Member).where(Member.user_id == user_id, Member.shift_id == shift_id)
        )
        return member.scalars().first()

    async def add_one_lombaryer(self, member: Member) -> None:
        if not member.numbers_lombaryers:
            member.numbers_lombaryers = 1
        else:
            member.numbers_lombaryers += 1
        await self._session.merge(member)
        await self._session.commit()

    async def create_all(self, member_list: tuple[Member]) -> tuple[Member]:
        self._session.add_all(member_list)
        await self._session.commit()
        return member_list
