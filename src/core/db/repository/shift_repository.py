from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.request_models.shift import ShiftSortRequest
from src.api.response_models.shift import ShiftDtoRespone
from src.core.db.db import get_session
from src.core.db.models import Member, Request, Shift, User
from src.core.db.repository import AbstractRepository
from src.core.exceptions import (
    GetStartedShiftException,
    NoShiftForRegistrationException,
    NotFoundException,
)
from src.core.settings import settings


class ShiftRepository(AbstractRepository):
    """Репозиторий для работы с моделью Shift."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Shift)

    async def get_with_members(self, id: UUID, member_status: Optional[Member.Status]) -> Shift:
        """Получить смену (Shift) по её id вместе со связанными данными.

        Связанные данные: Shift -> Memeber -> User, Shift -> Member -> Report.

        Аргументы:
            id (UUID) - id смены (shift)
            member_status (Optional[Member.Status]) - статус участника смены.
        """
        member_stmt = Shift.members
        if member_status:
            member_stmt = member_stmt.and_(Member.status == member_status)
        statement = (
            select(Shift)
            .where(Shift.id == id)
            .options(selectinload(member_stmt).selectinload(Member.reports))
            .options(selectinload(member_stmt).selectinload(Member.user))
        )
        request = await self._session.execute(statement)
        request = request.scalars().first()
        if request is None:
            raise NotFoundException(object_name=Shift.__doc__, object_id=id)
        return request

    async def list_all_requests(self, id: UUID, status: Optional[Request.Status]) -> list[ShiftDtoRespone]:
        db_list_request = await self._session.execute(
            select(
                Request.user_id,
                Request.id.label("request_id"),
                Request.status,
                User.name,
                User.surname,
                User.date_of_birth,
                User.city,
                User.phone_number.label("phone"),
            )
            .join(Request.user)
            .where(
                or_(Request.shift_id == id),
                # Добавление условия запроса к бд если есть статус,
                # а если нету то получение всех записей из бд по shift_id
                or_(status is None, Request.status == status),
            )
        )
        return db_list_request.all()

    async def get_shifts_with_total_users(
        self,
        status: Optional[Shift.Status],
        sort: Optional[ShiftSortRequest],
    ) -> list:
        shifts = (
            select(
                Shift.id,
                Shift.status.label('status'),
                Shift.started_at,
                Shift.finished_at,
                Shift.title,
                Shift.final_message,
                Shift.sequence_number,
                func.count(Request.user_id).label('total_users'),
            )
            .outerjoin(Shift.requests)
            .group_by(Shift.id)
            .where(
                or_(status is None, Shift.status == status),
            )
            .order_by(sort or Shift.started_at.desc())
        )
        shifts = await self._session.execute(shifts)
        return shifts.all()

    async def get_started_shift_id(self) -> UUID:
        """Возвращает id активной на данный момент смены."""
        shift_id = await self._session.scalars(select(Shift.id).where(Shift.status == Shift.Status.STARTED))
        shift_id = shift_id.first()
        if not shift_id:
            raise GetStartedShiftException(detail='Активной смены не найдено.')
        return shift_id

    async def get_open_for_registration_shift_id(self) -> UUID | None:
        can_be_added_to_active_shift = (
            Shift.started_at + timedelta(days=settings.DAYS_FROM_START_OF_SHIFT_TO_JOIN) >= date.today()
        )
        statement = select(Shift.id).where(
            or_(
                and_(Shift.status == Shift.Status.STARTED, can_be_added_to_active_shift),
                Shift.status == Shift.Status.PREPARING,
            ),
        )
        shift_id = await self._session.execute(statement)
        shift_id = shift_id.scalars().first()
        if not shift_id:
            raise NoShiftForRegistrationException
        return shift_id
