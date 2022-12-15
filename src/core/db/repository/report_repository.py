from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.response_models.report import ReportResponse
from src.api.response_models.task import LongTaskResponse
from src.core.db import DTO_models
from src.core.db.db import get_session
from src.core.db.models import Member, Report, Shift, Task, User
from src.core.db.repository import AbstractRepository
from src.core.exceptions import CurrentTaskNotFoundError
from src.core.settings import settings


class ReportRepository(AbstractRepository):
    """Репозиторий для работы с моделью Report."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Report)

    async def get_by_report_url(self, url: str) -> Report:
        reports = await self._session.execute(select(Report).where(Report.report_url == url))
        return reports.scalars().first()

    async def get_report_with_report_url(
        self,
        id: UUID,
    ) -> ReportResponse:
        """Получить отчет участника по id с url фото выполненного задания."""
        report = await self._session.execute(
            select(Report).options(selectinload(Report.member).selectinload(Member.user)).where(Report.id == id)
        )
        report = report.scalars().first()
        return ReportResponse.parse_from(report)

    async def get_all_ids(
        self,
        shift_id: UUID,
        task_date: date,
    ) -> list[tuple[int]]:
        """Получить список кортежей с id всех Report, id всех юзеров и id задач этих юзеров."""
        reports_info = await self._session.execute(
            select(Report.id, Member.user_id, Report.task_id)
            .where(
                and_(
                    Report.shift_id == shift_id,
                    Report.task_date == task_date,
                    Report.status == Report.Status.REVIEWING,
                )
            )
            .join(Member)
            .where(Report.member_id == Member.id)
            .order_by(Report.id)
        )
        return reports_info.all()

    async def get_all_tasks_id_under_review(self) -> Optional[list[UUID]]:
        """Получить список id непроверенных задач."""
        all_tasks_id_under_review = await self._session.execute(
            select(Report.task_id).select_from(Report).where(Report.status == Report.Status.REVIEWING)
        )
        return all_tasks_id_under_review.all()

    async def get_tasks_by_report_ids(self, report_ids: list[UUID]) -> list[LongTaskResponse]:
        """Получить список заданий с подробностями на каждого участника по report_id."""
        tasks = await self._session.execute(
            select(
                Task.id.label("task_id"),
                Task.url.label("task_url"),
                Task.description.label("task_description"),
                User.telegram_id.label("user_telegram_id"),
            )
            .where(Report.id.in_(report_ids))
            .join(Report.task)
            .join(Report.member)
            .join(Member.user)
        )
        tasks = tasks.all()
        task_infos = []
        for task in tasks:
            task_info = LongTaskResponse(**task)
            task_infos.append(task_info)
        return task_infos

    async def create_all(self, reports_list: list[Report]) -> Report:
        self._session.add_all(reports_list)
        await self._session.commit()
        return reports_list

    async def get_summaries_of_reports(self, shift_id: UUID, status: Report.Status) -> list[DTO_models.FullReportDto]:
        """Получить отчеты участников по id смены с url фото выполненного задания."""
        stmt = select(
            Shift.id,
            Shift.status,
            Shift.started_at,
            Report.id,
            Report.created_at,
            User.name,
            User.surname,
            Report.task_id,
            Task.description,
            Task.url,
            Report.report_url.label("photo_url"),
        )
        if shift_id:
            stmt = stmt.where(Report.shift_id == shift_id)
        if status:
            stmt = stmt.where(Report.status == status)
        stmt = stmt.join(Shift).join(Member).join(User).join(Task).order_by(desc(Shift.started_at))
        reports = await self._session.execute(stmt)
        return [DTO_models.FullReportDto(*report) for report in reports.all()]

    async def get_members_ids_for_excluding(self, shift_id: UUID, task_amount: int) -> list[UUID]:
        """Возвращает список id участников, кто не отправлял отчеты на задания указанное количество раз.

        Аргументы:
            shift_id (UUID): id стартовавшей смены
            task_amount (int): количество пропущенных заданий подряд, при котором участник считается неактивным.
        """
        subquery_rank = (
            select(
                func.rank().over(order_by=Report.task_date.desc(), partition_by=Report.user_id).label('rnk'),
                Report.user_id,
                Report.status,
            )
            .where(
                and_(
                    Report.shift_id == shift_id,
                )
            )
            .subquery()
        )
        subquery_last_statuses = select(subquery_rank).where(subquery_rank.c.rnk <= task_amount).subquery()
        case_statement = case(
            (subquery_last_statuses.c.status == Report.Status.WAITING, 1),
        )
        statement = (
            select(subquery_last_statuses.c.user_id)
            .having(func.count(case_statement) >= task_amount)
            .group_by(subquery_last_statuses.c.user_id)
        )
        return (await self._session.scalars(statement)).all()

    async def get_current_report(self, user_id: UUID) -> Report:
        now = datetime.now()
        task_date = now.date() if now.hour >= settings.SEND_NEW_TASK_HOUR else now.date() - timedelta(days=1)
        reports = await self._session.execute(
            select(Report).where(
                Report.user_id == user_id,
                Report.task_date == task_date,
            )
        )
        report = reports.scalars().first()
        if not report:
            raise CurrentTaskNotFoundError()
        return report
