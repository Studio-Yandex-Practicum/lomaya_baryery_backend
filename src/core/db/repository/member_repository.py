from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.db.db import get_session
from src.core.db.models import Member, Report, Task
from src.core.db.repository import AbstractRepository
from src.core.exceptions import NotFoundException
from src.core.utils import get_current_task_date


class MemberRepository(AbstractRepository):
    """Репозиторий для работы с моделью Member."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Member)

    async def get_by_user_and_shift(self, shift_id: UUID, user_id: UUID) -> Member:
        member = await self._session.execute(
            select(Member).where(Member.shift_id == shift_id, Member.user_id == user_id)
        )
        return member.scalars().first()

    async def get_with_user(self, id: UUID) -> Member:
        member = await self._session.execute(select(Member).where(Member.id == id).options(selectinload(Member.user)))
        member = member.scalars().first()
        if not member:
            raise NotFoundException(object_name=Member.__name__, object_id=id)
        return member

    async def get_members_for_excluding(self, shift_id: UUID, task_amount: int) -> list[Member]:
        members = self._session.scalars(
            select(Member)
            .where(
                Member.shift_id == shift_id,
                Member.status == Member.Status.ACTIVE,
                Report.status == Report.Status.WAITING,
                Report.task_date >= func.current_date() - task_amount,
            )
            .join(Report)
            .group_by(Member)
            .having(func.count() == task_amount)
        )
        return members.all()

    async def get_members_for_reminding(self, shift_id: UUID, task: Task) -> list[Member]:
        current_task_date = get_current_task_date()
        members = await self._session.scalars(
            select(Member)
            .where(
                Member.shift_id == shift_id,
                Member.status == Member.Status.ACTIVE,
                Report.status == Report.Status.WAITING,
                Report.task_date == current_task_date
            )
        )
        return members.all()
