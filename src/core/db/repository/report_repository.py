from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import DTO_models
from src.core.db.db import get_session
from src.core.db.models import Member, Report, Shift, Task, User
from src.core.db.repository import AbstractRepository
from src.core.exceptions import CurrentTaskNotFoundError
from src.core.utils import get_current_task_date


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
    ) -> dict:
        """Получить отчет участника по id с url фото выполненного задания."""
        report = await self._session.execute(
            select(
                Report.user_id,
                Report.id,
                Report.task_id,
                Report.task_date,
                Report.status,
                Report.report_url.label("photo_url"),
            ).where(Report.id == id)
        )
        report = report.all()
        return dict(*report)

    async def get_all_tasks_id_under_review(self) -> Optional[list[UUID]]:
        """Получить список id непроверенных задач."""
        all_tasks_id_under_review = await self._session.execute(
            select(Report.task_id).select_from(Report).where(Report.status == Report.Status.REVIEWING)
        )
        return all_tasks_id_under_review.all()

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
        stmt = stmt.join(Shift).join(User).join(Task).order_by(desc(Shift.started_at))
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
        """Получить текущий отчет по id пользователя."""
        reports = await self._session.execute(
            select(Report).where(
                Report.member_id.in_(select(Member.id).where(Member.user_id == user_id)),
                Report.task_date == get_current_task_date(),
            )
        )
        report = reports.scalars().first()
        if not report:
            raise CurrentTaskNotFoundError()
        return report
