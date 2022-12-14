from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Member
from src.core.db.repository import AbstractRepository


class MemberRepository(AbstractRepository):
    """Репозиторий для работы с моделью Member."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Member)

    async def get_by_user_and_shift(self, shift_id: UUID, user_id: UUID) -> Member:
        member = await self._session.execute(
            select(Member).where(Member.shift_id == shift_id, Member.user_id == user_id)
        )
        return member.scalars().first()

    async def set_members_excluded(self, user_ids: list[UUID], shift_id: UUID) -> None:
        """Устанавливает участникам смены статус excluded.

        Аргументы:
            user_ids (list[UUID]): список id участников
            shift_id (UUID): id смены
        """
        statement = (
            update(Member)
            .where(
                and_(
                    Member.user_id.in_(user_ids),
                    Member.shift_id == shift_id,
                )
            )
            .values(status=Member.Status.EXCLUDED)
        )
        await self._session.execute(statement)
        await self._session.commit()
