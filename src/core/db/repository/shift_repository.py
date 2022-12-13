from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.request_models.shift import ShiftSortRequest
from src.api.response_models.shift import ShiftDtoRespone
from src.core.db.db import get_session
from src.core.db.models import Member, Report, Request, Shift, User
from src.core.db.repository import AbstractRepository
from src.core.exceptions import NotFoundException


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
                Shift.status,
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

    async def get_today_active_report_ids(self) -> list[UUID]:
        task_date = datetime.now().date()
        active_task_ids = await self._session.execute(
            select(Report.id)
            .where(Report.task_date == task_date, Request.status == Request.Status.APPROVED.value)
            .join(Shift.reports)
            .join(Shift.requests)
        )
        return active_task_ids.scalars().all()

    async def get_started_shift_id(self) -> list[UUID]:
        """Возвращает id активной на данный момент смены."""
        statement = select(Shift.id).where(and_(Shift.status == Shift.Status.STARTED))
        return (await self._session.scalars(statement)).first()
