from datetime import date, timedelta
from typing import Sequence
from urllib.parse import urljoin

from fastapi import Depends
from pydantic.schema import UUID
from telegram.ext import Application

from src.api.response_models.report import ReportResponse
from src.bot import services
from src.core import exceptions
from src.core.db import DTO_models
from src.core.db.models import Member, Report, Shift, Task
from src.core.db.repository import MemberRepository, ReportRepository, ShiftRepository
from src.core.services.task_service import TaskService
from src.core.settings import settings
from src.core.utils import get_current_task_date, get_lombaryers_for_quantity


class ReportService:
    """Вспомогательный класс для Report.

    Внутри реализованы методы для формирования итогового
    отчета с информацией о смене и непроверенных задачах пользователей
    с привязкой к смене и дню.
    """

    def __init__(
        self,
        report_repository: ReportRepository = Depends(),
        shift_repository: ShiftRepository = Depends(),
        member_repository: MemberRepository = Depends(),
        task_service: TaskService = Depends(),
    ) -> None:
        self.__telegram_bot = services.BotService
        self.__report_repository = report_repository
        self.__shift_repository = shift_repository
        self.__member_repository = member_repository
        self.__task_service = task_service

    async def get_report(self, id: UUID) -> Report:
        return await self.__report_repository.get(id)

    async def check_duplicate_report(self, url: str) -> None:
        report = await self.__report_repository.get_by_report_url(url)
        if report:
            raise exceptions.DuplicateReportError

    async def check_report_skipped(self, report: Report) -> None:
        if report.status == Report.Status.SKIPPED:
            raise exceptions.ReportAlreadySkippedError

    async def get_today_task_and_active_members(
        self, shift: Shift, current_day_of_month: int
    ) -> tuple[Task, list[Member]]:
        """Получить ежедневное задание и список активных участников смены."""
        members = await self.__member_repository.get_active_members_for_shift(shift.id)
        task = await self.__task_service.get_task_by_day_of_month(shift.tasks, current_day_of_month)
        return task, members

    async def approve_report(self, report_id: UUID, administrator_id: UUID, bot: Application) -> ReportResponse:
        """Задание принято: изменение статуса, начисление 1 /"ломбарьерчика/", уведомление участника."""
        report = await self.__report_repository.get(report_id)
        self.__can_change_status(report.status)
        report.status = Report.Status.APPROVED
        report.set_reviewer(administrator_id)
        report = await self.__report_repository.update(report_id, report)
        member = await self.__member_repository.get_with_user_and_shift(report.member_id)
        member.numbers_lombaryers += 1
        await self.__member_repository.update(member.id, member)
        await self.__telegram_bot(bot).notify_approved_task(member.user, report, member.shift)
        await self.__notify_member_about_finished_shift(member, bot)
        return report

    async def decline_report(self, report_id: UUID, administrator_id: UUID, bot: Application) -> ReportResponse:
        """Задание отклонено: изменение статуса, уведомление участника в телеграм."""
        report = await self.__report_repository.get(report_id)
        self.__can_change_status(report.status)
        report.status = Report.Status.DECLINED
        report.set_reviewer(administrator_id)
        report = await self.__report_repository.update(report_id, report)
        member = await self.__member_repository.get_with_user_and_shift(report.member_id)
        await self.__telegram_bot(bot).notify_declined_task(member.user, member.shift, report)
        await self.__notify_member_about_finished_shift(member, bot)
        return report

    async def skip_current_report(self, user_id: UUID) -> Report:
        """Задание пропущено: изменение статуса."""
        report = await self.__report_repository.get_current_report(user_id)
        if report.status is Report.Status.SKIPPED:
            raise exceptions.ReportAlreadySkippedError
        if report.status is not Report.Status.WAITING:
            raise exceptions.ReportCantBeSkippedError
        report.status = Report.Status.SKIPPED
        return await self.__report_repository.update(report.id, report)

    async def __notify_member_about_finished_shift(self, member: Member, bot: Application) -> None:
        """Уведомляет пользователя об окончании смены, если у него не осталось непроверенных заданий."""
        if (
            member.shift.status is Shift.Status.READY_FOR_COMPLETE
            and not await self.__member_repository.is_unreviewed_report_exists(member.id)
        ):
            await self.__finish_shift_with_all_reports_reviewed(member.shift)
            await self.__telegram_bot(bot).send_message(
                member.user,
                member.shift.final_message.format(
                    name=member.user.name,
                    surname=member.user.surname,
                    numbers_lombaryers=member.numbers_lombaryers,
                    lombaryers_case=get_lombaryers_for_quantity(member.numbers_lombaryers),
                ),
            )

    def __can_change_status(self, status: Report.Status) -> None:
        """Проверка статуса задания перед изменением."""
        if status in (Report.Status.APPROVED, Report.Status.DECLINED):
            raise exceptions.ReportAlreadyReviewedError
        if status is Report.Status.WAITING:
            raise exceptions.ReportWaitingPhotoError

    async def __finish_shift_with_all_reports_reviewed(self, shift: Shift) -> None:
        """Закрывает смену, если не осталось непроверенных заданий."""
        if not await self.__shift_repository.is_unreviewed_report_exists(shift.id):
            shift.status = Shift.Status.FINISHED
            await self.__shift_repository.update(shift.id, shift)

    async def get_summaries_of_reports(
        self,
        shift_id: UUID,
        status: Report.Status,
    ) -> list[DTO_models.FullReportDto]:
        """Получает из БД список отчетов участников.

        Список берется по id смены и/или статусу заданий с url фото выполненного задания.
        """
        shift_exists = await self.__shift_repository.check_shift_existence(shift_id)
        if not shift_exists:
            raise exceptions.ObjectNotFoundError(Shift, shift_id)
        reports = await self.__report_repository.get_summaries_of_reports(shift_id, status)
        for report in reports:
            report.task_url = urljoin(settings.APPLICATION_URL, report.task_url)
            if report.photo_url:
                report.photo_url = urljoin(settings.APPLICATION_URL, report.photo_url)
        return reports

    async def get_current_report(self, user_id: UUID) -> Report:
        return await self.__report_repository.get_current_report(user_id)

    async def send_report(self, report: Report, photo_url: str) -> Report:
        await self.check_report_skipped(report)
        await self.check_duplicate_report(photo_url)
        report.send_report(photo_url)
        return await self.__report_repository.update(report.id, report)

    async def create_daily_reports(self, members: list[Member], task: Task) -> None:
        current_date = date.today()
        reports = [
            Report(
                shift_id=member.shift_id,
                task_id=task.id,
                status=(
                    Report.Status.WAITING if member.status == Member.Status.ACTIVE else Report.Status.NOT_PARTICIPATE
                ),
                task_date=current_date,
                member_id=member.id,
            )
            for member in members
        ]
        await self.__report_repository.create_all(reports)

    async def __get_waiting_reports(self) -> Sequence[Report]:
        """Получаем список отчетов участников со статусом waiting."""
        return await self.__report_repository.get_waiting_reports()

    async def set_status_to_waiting_reports(self, status: Report.Status):
        """Устанавливаем статус всем отчетам со статусом waiting."""
        reports_list = await self.__get_waiting_reports()
        return await self.__report_repository.set_status_to_reports(reports_list, status)

    async def create_not_participated_reports(self, member_id: UUID, shift: Shift) -> None:
        """Создаем пропущенные отчеты со статусом not_participate участнику, который пришел на смену позже."""
        count_of_missed_days = (get_current_task_date() - shift.started_at).days
        reports = [
            Report(
                shift_id=shift.id,
                task_id=shift.tasks[str((shift.started_at + timedelta(days=day)).day)],
                status=Report.Status.NOT_PARTICIPATE,
                task_date=shift.started_at + timedelta(days=day),
                member_id=member_id,
            )
            for day in range(0, count_of_missed_days + 1)
        ]
        await self.__report_repository.create_all(reports)

    async def is_previous_report_not_submitted(self, member_id: UUID) -> bool:
        """Проверяет статус вчерашнего отчета."""
        return await self.__report_repository.is_previous_report_not_submitted(member_id)
