from http import HTTPStatus
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Member, Request
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

    async def create_members(self, shift_id: UUID) -> None:
        approved_requests = await self._session.execute(
            select(Request).where(Request.status == Request.Status.APPROVED.value, Request.shift_id == shift_id)
        )
        approved_requests = approved_requests.scalars().all()
        if not approved_requests:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Для смены id={shift_id} заявки со статусом {Request.Status.APPROVED.value} не найдены.",
            )
        for request in approved_requests:
            member_data = {
                'user_id': request.user_id,
                'shift_id': shift_id,
                'numbers_lombaryers': 0,
                'status': Member.Status.ACTIVE.value,
            }
            new_member = Member(**member_data)
            await self.create(new_member)
