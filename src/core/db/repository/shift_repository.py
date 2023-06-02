from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, subqueryload

from src.api.request_models.shift import ShiftSortRequest
from src.api.response_models.shift import ShiftDtoResponse
from src.core import exceptions
from src.core.db.db import get_session
from src.core.db.DTO_models import ShiftAnalyticReportDto
from src.core.db.models import Member, Report, Request, Shift, Task, User
from src.core.db.repository import AbstractRepository
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
            raise exceptions.ObjectNotFoundError(Shift, id)
        return request

    async def list_all_requests(self, id: UUID, status: Optional[Request.Status]) -> list[ShiftDtoResponse]:
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
        status: Optional[list[Shift.Status]],
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
                func.count(Member.user_id).label('total_users'),
            )
            .outerjoin(Shift.members)
            .group_by(Shift.id)
            .where(status is None or Shift.status.in_(status))
            .order_by(sort or Shift.started_at.desc())
        )
        shifts = await self._session.execute(shifts)
        return shifts.all()

    async def get_started_shift_id(self) -> UUID:
        """Возвращает id активной на данный момент смены."""
        shift_id = await self._session.scalars(select(Shift.id).where(Shift.status == Shift.Status.STARTED))
        shift_id = shift_id.first()
        if not shift_id:
            raise exceptions.ShiftNotFoundError
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
            raise exceptions.RegistrationForbiddenError
        return shift_id

    async def get_shift_with_status_or_none(self, status: Shift.Status) -> Optional[Shift]:
        """Возвращает смену с заданным статусом."""
        statement = select(Shift).where(Shift.status == status)
        return (await self._session.scalars(statement)).first()

    async def get_shift_with_request(self, id: UUID) -> Shift:
        """Получить смену (Shift) по её id вместе со связанными данными.

        Связанные данные: Shift -> Request.

        Аргументы:
            id (UUID) - id смены (shift)
        """
        statement = select(Shift).where(Shift.id == id).options(selectinload(Shift.requests))
        request = await self._session.execute(statement)
        request = request.scalars().first()
        if request is None:
            raise exceptions.ObjectNotFoundError(Shift, id)
        return request

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

    async def get_active_or_complete_shift(self) -> Optional[Shift]:
        """Возвращает активную смену или смену, приготовленную к закрытию."""
        statement = select(Shift).where(
            or_(
                Shift.status == Shift.Status.READY_FOR_COMPLETE,
                Shift.status == Shift.Status.STARTED,
            ),
        )
        return (await self._session.scalars(statement)).first()

    async def get_preparing_shift_with_started_at_today(self) -> Optional[Shift]:
        """Возвращает смену, если смена имеет статус preparing и дата старта совпадает с текущим днём."""
        statement = select(Shift).where(
            and_(
                Shift.status == Shift.Status.PREPARING,
                Shift.started_at == date.today(),
            ),
        )
        return await self._session.scalar(statement)

    async def get_shift_statistics_report_by_id(self, shift_id: UUID):
        """Отчёт по задачам из выбранной смены.

        Содержит:
        - список всех задач;
        - количество отчетов принятых с 1-й/2-й/3-й попытки;
        - общее количество принятых/отклонённых/не предоставленных отчётов по каждому заданию.
        """
        stmt = (
            select(
                Task.sequence_number,
                Task.title,
                func.count().filter(Report.number_attempt == 0).label('approved_from_1_attempt'),
                func.count().filter(Report.number_attempt == 1).label('approved_from_2_attempt'),
                func.count().filter(Report.number_attempt == 2).label('approved_from_3_attempt'),
                func.count().filter(Report.status == Report.Status.APPROVED).label(Report.Status.APPROVED),
                func.count().filter(Report.status == Report.Status.DECLINED).label(Report.Status.DECLINED),
                func.count().filter(Report.status == Report.Status.SKIPPED).label(Report.Status.SKIPPED),
                func.count().label('reports_total'),
            )
            .where(Report.shift_id == shift_id)
            .join(Task.reports)
            .group_by(Task.title, Task.sequence_number)
            .order_by(Task.sequence_number)
        )
        reports = await self._session.execute(stmt)
        return tuple(ShiftAnalyticReportDto(*report) for report in reports.all())

    async def get_all_reports_of_member(self, shift_id: UUID, member_id: UUID) -> list[Report]:
        stmt = (
            select(Report).where(Report.shift_id == shift_id, Report.member_id == member_id).order_by(Report.task_date)
        )
        reports = await self._session.execute(stmt)
        return reports.scalars().all()
