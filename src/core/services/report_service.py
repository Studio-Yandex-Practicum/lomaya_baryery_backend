from datetime import date
from urllib.parse import urljoin

from fastapi import Depends
from pydantic.schema import UUID
from telegram.ext import Application

from src.api.response_models.report import ReportResponse
from src.bot import services
from src.core.db import DTO_models
from src.core.db.models import Member, Report, Shift, Task
from src.core.db.repository import MemberRepository, ReportRepository, ShiftRepository
from src.core.exceptions import (
    DuplicateReportError,
    NotFoundException,
    ReportAlreadyReviewedException,
    ReportSkippedError,
    ReportWaitingPhotoException,
)
from src.core.services.task_service import TaskService
from src.core.settings import settings


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

    async def get_report_with_report_url(self, id: UUID) -> ReportResponse:
        return await self.__report_repository.get_report_with_report_url(id)

    async def check_duplicate_report(self, url: str) -> None:
        report = await self.__report_repository.get_by_report_url(url)
        if report:
            raise DuplicateReportError()

    async def check_report_skipped(self, report: Report) -> None:
        if report.status == Report.Status.SKIPPED:
            raise ReportSkippedError()

    async def get_today_task_and_active_members(self, current_day_of_month: int) -> tuple[Task, list[Member]]:
        """Получить ежедневное задание и список активных участников смены."""
        shift_id = await self.__shift_repository.get_started_shift_id()
        shift = await self.__shift_repository.get_with_members(shift_id, Member.Status.ACTIVE)
        task = await self.__task_service.get_task_by_day_of_month(shift.tasks, current_day_of_month)
        return task, shift.members

    async def approve_report(self, report_id: UUID, bot: Application) -> ReportResponse:
        """Задание принято: изменение статуса, начисление 1 /"ломбарьерчика/", уведомление участника."""
        report = await self.__report_repository.get(report_id)
        self.__can_change_status(report.status)
        report.status = Report.Status.APPROVED
        report = await self.__report_repository.update(report_id, report)
        member = await self.__member_repository.get_with_user_and_shift(report.member_id)
        member.numbers_lombaryers += 1
        await self.__member_repository.update(member.id, member)
        await self.__telegram_bot(bot).notify_approved_task(member.user, report, member.shift)
        await self.__notify_member_about_finished_shift(member, bot)
        return report

    async def decline_report(self, report_id: UUID, bot: Application) -> ReportResponse:
        """Задание отклонено: изменение статуса, уведомление участника в телеграм."""
        report = await self.__report_repository.get(report_id)
        self.__can_change_status(report.status)
        report.status = Report.Status.DECLINED
        report = await self.__report_repository.update(report_id, report)
        member = await self.__member_repository.get_with_user_and_shift(report.member_id)
        await self.__telegram_bot(bot).notify_declined_task(member.user, member.shift)
        await self.__notify_member_about_finished_shift(member, bot)
        return report

    async def skip_report(self, user_id: UUID) -> Report:
        """Задание пропущено: изменение статуса."""
        report = await self.__report_repository.get_current_report(user_id)
        if report.status is not Report.Status.WAITING:
            raise ReportAlreadyReviewedException(status=report.status)
        report.status = Report.Status.SKIPPED
        return await self.__report_repository.update(report.id, report)

    async def __notify_member_about_finished_shift(self, member: Member, bot: Application) -> None:
        """Уведомляет пользователя об окончании смены, если у него не осталось непроверенных заданий."""
        if (
            member.shift.status is Shift.Status.READY_FOR_COMPLETE
            and not await self.__member_repository.is_unreviewed_report_exists(member.id)
        ):
            await self.__finish_shift_with_all_reports_reviewed(member.shift)
            await self.__telegram_bot(bot).send_message(member.user, member.shift.final_message)

    def __can_change_status(self, status: Report.Status) -> None:
        """Проверка статуса задания перед изменением."""
        if status in (Report.Status.APPROVED, Report.Status.DECLINED):
            raise ReportAlreadyReviewedException(status=status)
        if status is Report.Status.WAITING:
            raise ReportWaitingPhotoException

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
            raise NotFoundException(object_name=Shift.__name__, object_id=shift_id)
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
                status=Report.Status.WAITING,
                task_date=current_date,
                member_id=member.id,
            )
            for member in members
        ]
        await self.__report_repository.create_all(reports)
