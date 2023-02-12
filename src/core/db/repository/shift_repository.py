from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, subqueryload

from src.api.request_models.shift import ShiftSortRequest
from src.api.response_models.shift import ShiftDtoRespone
from src.core.db.db import get_session
from src.core.db.models import Member, Report, Request, Shift, User
from src.core.db.repository import AbstractRepository
from src.core.exceptions import (
    GetStartedShiftException,
    NotFoundException,
    RegistrationForbidenException,
)
from src.core.settings import settings


class ShiftRepository(AbstractRepository):
    """Репозиторий для работы с моделью Shift."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Shift)

    async def get_with_members(self, id: UUID, member_status: Optional[Member.Status]) -> Shift:
        """Получить смену (Shift) по её id вместе со связанными данными.

        Связанные данные: Shift -> Member -> User, Shift -> Member -> Report.

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
                Request.status.label("request_status"),
                User.name,
                User.surname,
                User.date_of_birth,
                User.city,
                User.phone_number,
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

    async def get_open_for_registration_shift_id(self) -> UUID:
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
            raise RegistrationForbidenException
        return shift_id

    async def get_shift_with_status_or_none(self, status: Shift.Status) -> Optional[Shift]:
        """Возвращает смену с заданным статусом."""
        statement = select(Shift).where(Shift.status == status)
        return (await self._session.scalars(statement)).first()

    async def check_shift_existence(self, shift_id: UUID) -> bool:
        shift_exists = await self._session.execute(select(select(Shift).where(Shift.id == shift_id).exists()))
        return shift_exists.scalar()

    async def get_with_members_with_reviewed_reports(self, shift_id: UUID) -> Shift:
        """Возвращает смену с активными участниками, у которых все задания проверены."""
        members_id = (
            select(Member.id)
            .join(Report)
            .where(
                Member.shift_id == shift_id,
                Member.status == Member.Status.ACTIVE,
                Report.member_id == Member.id,
                Report.status == Report.Status.REVIEWING,
            )
            .group_by(Member.id)
            .subquery()
        )
        shift = await self._session.execute(
            select(Shift)
            .where(Shift.id == shift_id)
            .options(subqueryload(Shift.members.and_(Member.id.notin_(members_id))).subqueryload(Member.user))
        )
        return shift.scalars().first()

    async def get_with_members_and_unreviewed_reports(self, shift_id: UUID) -> Shift:
        """Возвращает смену с активными участниками и их непроверенными заданиями."""
        members_id = (
            select(Member.id)
            .join(Report)
            .where(
                Member.shift_id == shift_id,
                Member.status == Member.Status.ACTIVE,
                Report.member_id == Member.id,
                Report.status == Report.Status.REVIEWING,
            )
            .group_by(Member.id)
            .subquery()
        )
        member_stmt = Shift.members.and_(Member.id.in_(members_id))
        shift = await self._session.execute(
            select(Shift)
            .where(Shift.id == shift_id)
            .options(subqueryload(member_stmt).subqueryload(Member.user))
            .options(
                subqueryload(member_stmt).subqueryload(Member.reports.and_(Report.status == Report.Status.REVIEWING))
            )
        )
        return shift.scalars().first()

    async def is_unreviewed_report_exists(self, shift_id: UUID) -> bool:
        """Проверяет, остались ли непроверенные задачи в смене."""
        stmt = select(Report).where(Report.status == Report.Status.REVIEWING, Report.shift_id == shift_id)
        report_under_review = await self._session.execute(select(stmt.exists()))
        return report_under_review.scalar()
