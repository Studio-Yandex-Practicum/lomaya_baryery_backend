from typing import Optional, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import asc, case, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.request_models.user import UserDescAscSortRequest, UserFieldSortRequest
from src.core.db.db import get_session
from src.core.db.DTO_models import (
    ShiftByUserWithReportSummaryDto,
    UserAnalyticReportDto,
)
from src.core.db.models import Member, Report, Request, Shift, Task, User
from src.core.db.repository import AbstractRepository


class UserRepository(AbstractRepository):
    """Репозиторий для работы с моделью User."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, User)

    async def get_user_shifts_detail(self, user_id: UUID) -> list[ShiftByUserWithReportSummaryDto]:
        """
        Получить список смен, участником которых является пользователь.

        К каждой смене добавляются дополнительные поля:
        numbers_lombaryers -- количество "ломбарьерчиков",
        total_approved -- количество одобренных заданий,
        total_declined -- количество отмененных заданий,
        total_skipped -- количество пропущенных заданий,
        is_excluded -- был ли участник исключен из смены (bool).
        """
        stmt = (
            select(
                Shift.id,
                Shift.title,
                Shift.started_at,
                Shift.finished_at,
                Member.numbers_lombaryers,
                Member.id,
                func.count(case(((Report.status == "approved"), Report.id))).label("total_approved"),
                func.count(case(((Report.status == "declined"), Report.id))).label("total_declined"),
                func.count(case(((Report.status == "waiting"), Report.id))).label("total_skipped"),
                case(((Member.status == "excluded"), True), else_=False).label("is_excluded"),
            )
            .join(User.members, isouter=True)
            .join(Member.shift, isouter=True)
            .join(Member.reports, isouter=True)
            .group_by(Member.numbers_lombaryers, Member.status, Shift.id, Member.id)
            .where(User.id == user_id)
        )
        list_user_shifts = await self._session.execute(stmt)
        return [ShiftByUserWithReportSummaryDto(*shift) for shift in list_user_shifts if shift.id is not None]

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        user = await self._session.execute(select(User).where(User.telegram_id == telegram_id))
        return user.scalars().first()

    async def check_user_existence(self, telegram_id: int, phone_number: str) -> bool:
        user_exists = await self._session.execute(
            select(
                select(User)
                .where(
                    or_(
                        User.phone_number == phone_number,
                        User.telegram_id == telegram_id,
                    )
                )
                .exists()
            )
        )
        return user_exists.scalar()

    async def get_users_with_status(
        self,
        status: Optional[User.Status] = None,
        field_sort: Optional[UserFieldSortRequest] = None,
        direction_sort: Optional[UserDescAscSortRequest] = None,
    ) -> list[User]:
        sorting = {'desc': desc, 'asc': asc}
        users = await self._session.execute(
            select(
                User.id,
                User.name,
                User.surname,
                User.date_of_birth,
                User.city,
                User.phone_number,
                User.status,
                func.count(Member.shift).label('shifts_count'),
                case(
                    (
                        ((func.count(Shift.status).filter(Shift.status == Shift.Status.STARTED)) == 1),
                        True,
                    ),
                    else_=False,
                ).label("is_in_active_shift"),
            )
            .join(User.members, isouter=True)
            .join(Member.shift, isouter=True)
            .group_by(User.id)
            .where(
                or_(status is None, User.status == status),
                User.is_test_user == False,  # noqa
            )
            .order_by(sorting[direction_sort.value if direction_sort else 'asc'](field_sort or User.created_at))
        )
        return users.all()

    async def get_users_by_shift_id(self, shift_id: UUID) -> list[User]:
        users = await self._session.execute(
            select(User).where(
                User.id.in_(
                    select(Request.user_id).where(
                        Request.shift_id == shift_id
                    )
                )
            )
        )

        return users.scalars().all()

    async def get_test_users(self) -> list[User]:
        users = await self._session.execute(select(User).where(User.is_test_user == True))  # noqa
        return users.scalars().all()

    async def get_user_task_statistics_by_id_and_shift(self, user_id: UUID, shift_id: Optional[UUID] = None):
        """Отчёт по задачам участника.

        Содержит:
        - список *всех* задач;
        - количество отчетов принятых с 1-й/2-й/3-й попытки;
        - общее количество принятых/отклонённых/не предоставленных отчётов по каждому заданию.
        """
        sub_stmt = select(Member.id).filter(Member.user_id == user_id)
        if shift_id:
            sub_stmt = sub_stmt.filter(Member.shift_id == shift_id)

        stmt = (
            select(
                Task.sequence_number,
                Task.title,
                func.count(Report.id).filter(Report.number_attempt == 0).label('approved_from_1_attempt'),
                func.count(Report.id).filter(Report.number_attempt == 1).label('approved_from_2_attempt'),
                func.count(Report.id).filter(Report.number_attempt == 2).label('approved_from_3_attempt'),
                func.count(Report.id).filter(Report.status == Report.Status.APPROVED).label(Report.Status.APPROVED),
                func.count(Report.id).filter(Report.status == Report.Status.DECLINED).label(Report.Status.DECLINED),
                func.count(Report.id).filter(Report.status == Report.Status.SKIPPED).label(Report.Status.SKIPPED),
                func.count(Report.id).label('reports_total'),
            )
            .outerjoin(Task.reports.and_(Report.member_id.in_(sub_stmt)))
            .group_by(Task.sequence_number, Task.id)
            .order_by(Task.sequence_number)
        )
        reports = await self._session.execute(stmt)
        return tuple(UserAnalyticReportDto(*report) for report in reports.all())

    async def get_user_shift_statistics_by_id(self, user_id: UUID):
        """Отчёт по сменам участника.

        Содержит:
        - список смен, в которых участвует указанный пользователь;
        - количество отчетов принятых с 1-й/2-й/3-й попытки;
        - общее количество принятых/отклонённых/не предоставленных отчётов по каждому заданию.
        """
        stmt = (
            select(
                Shift.sequence_number,
                Shift.title,
                func.count(Report.id).filter(Report.number_attempt == 0).label('approved_from_1_attempt'),
                func.count(Report.id).filter(Report.number_attempt == 1).label('approved_from_2_attempt'),
                func.count(Report.id).filter(Report.number_attempt == 2).label('approved_from_3_attempt'),
                func.count(Report.id).filter(Report.status == Report.Status.APPROVED).label(Report.Status.APPROVED),
                func.count(Report.id).filter(Report.status == Report.Status.DECLINED).label(Report.Status.DECLINED),
                func.count(Report.id).filter(Report.status == Report.Status.SKIPPED).label(Report.Status.SKIPPED),
                func.count(Report.id).label('reports_total'),
            )
            .join(Shift.reports)
            .join(Report.member)
            .where(Member.user_id == user_id)
            .group_by(Shift.sequence_number, Shift.id)
            .order_by(Shift.sequence_number)
        )
        reports = await self._session.execute(stmt)
        return tuple(UserAnalyticReportDto(*report) for report in reports.all())

    async def get_user_shifts_titles(self, user_id: UUID) -> Sequence[Shift]:
        """Получить список смен заданного участника."""
        stmt = select(Shift).join(Member.shift).filter(Member.user_id == user_id)
        shifts = await self._session.execute(stmt)
        return shifts.scalars().all()
