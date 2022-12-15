from datetime import date
from typing import Any

from fastapi import Depends
from pydantic.schema import UUID
from telegram.ext import Application

from src.api.response_models.task import LongTaskResponse
from src.bot import services
from src.core.db import DTO_models
from src.core.db.models import Report
from src.core.db.repository import (
    MemberRepository,
    ReportRepository,
    ShiftRepository,
    TaskRepository,
    UserRepository,
)
from src.core.db.repository.request_repository import RequestRepository
from src.core.exceptions import (
    DuplicateReportError,
    ReportAlreadyReviewedException,
    ReportWaitingPhotoException,
)
from src.core.services.request_sevice import RequestService
from src.core.services.task_service import TaskService
from src.core.settings import settings


class ReportService:
    """Вспомогательный класс для Report.

    Внутри реализованы методы для формирования итогового
    отчета с информацией о смене и непроверенных задачах пользователей
    с привязкой к смене и дню.

    Метод 'get_tasks_report' формирует отчет с информацией о задачах
    и юзерах.
    Метод 'get' возвращает экземпляр Report по id.
    """

    def __init__(
        self,
        report_repository: ReportRepository = Depends(),
        task_repository: TaskRepository = Depends(),
        shift_repository: ShiftRepository = Depends(),
        task_service: TaskService = Depends(),
        request_service: RequestService = Depends(),
        request_repository: RequestRepository = Depends(),
        user_repository: UserRepository = Depends(),
        member_repository: MemberRepository = Depends(),
    ) -> None:
        self.__telegram_bot = services.BotService
        self.__report_repository = report_repository
        self.__task_repository = task_repository
        self.__shift_repository = shift_repository
        self.__task_service = task_service
        self.__request_service = request_service
        self.__request_repository = request_repository
        self.__user_repository = user_repository
        self.__member_repository = member_repository

    async def get_report(self, id: UUID) -> Report:
        return await self.__report_repository.get(id)

    async def get_report_with_report_url(self, id: UUID) -> dict:
        return await self.__report_repository.get_report_with_report_url(id)

    async def check_duplicate_report(self, url: str) -> None:
        report = await self.__report_repository.get_by_report_url(url)
        if report:
            raise DuplicateReportError()

    async def get_today_active_reports(self) -> list[LongTaskResponse]:
        report_ids = await self.__shift_repository.get_today_active_report_ids()
        return await self.__report_repository.get_tasks_by_report_ids(report_ids)

    # TODO переписать
    async def get_tasks_report(self, shift_id: UUID, task_date: date) -> list[dict[str, Any]]:
        """Формирует итоговый список 'tasks' с информацией о задачах и юзерах."""
        report_ids = await self.__report_repository.get_all_ids(shift_id, task_date)
        tasks = []
        if not report_ids:
            return tasks
        for report_id, user_id, task_id in report_ids:
            task = await self.__task_repository.get_tasks_report(user_id, task_id)
            task["id"] = report_id
            tasks.append(task)
        return tasks

    async def approve_report(self, report_id: UUID, bot: Application.bot) -> None:
        """Задание принято: изменение статуса, начисление 1 /"ломбарьерчика/", уведомление участника."""
        report = await self.__report_repository.get(report_id)
        self.__can_change_status(report.status)
        report.status = Report.Status.APPROVED
        await self.__report_repository.update(report_id, report)
        member = await self.__member_repository.get_with_user(report.member_id)
        member.numbers_lombaryers += 1
        await self.__member_repository.update(member.id, member)
        await self.__telegram_bot(bot).notify_approved_task(member.user, report)
        return

    async def decline_report(self, report_id: UUID, bot: Application.bot) -> None:
        """Задание отклонено: изменение статуса, уведомление участника в телеграм."""
        report = await self.__report_repository.get(report_id)
        self.__can_change_status(report.status)
        report.status = Report.Status.DECLINED
        await self.__report_repository.update(report_id, report)
        member = await self.__member_repository.get_with_user(report.member_id)
        await self.__telegram_bot(bot).notify_declined_task(member.user)
        return

    def __can_change_status(self, status: Report.Status) -> None:
        """Проверка статуса задания перед изменением."""
        if status in (Report.Status.APPROVED, Report.Status.DECLINED):
            raise ReportAlreadyReviewedException(status=status)
        if status is Report.Status.WAITING:
            raise ReportWaitingPhotoException

    async def get_summaries_of_reports(
        self,
        shift_id: UUID,
        status: Report.Status,
    ) -> list[DTO_models.FullReportDto]:
        """Получает из БД список отчетов участников.

        Список берется по id смены и/или статусу заданий с url фото выполненного задания.
        """
        return await self.__report_repository.get_summaries_of_reports(shift_id, status)

    async def check_members_activity(self, bot: Application.bot) -> None:
        """Проверяет участников в стартовавшей смене.

        Если участники не посылают отчет о выполненом задании указанное
        в настройках количество раз подряд, то они будут исключены из смены.
        """
        shift_id = await self.__shift_repository.get_started_shift_id()
        members_to_exclude = await self.__member_repository.get_members_for_excluding(
            shift_id, settings.SEQUENTIAL_TASKS_PASSES_FOR_EXCLUDE
        )
        if len(members_to_exclude) > 0:
            await self.__request_service.exclude_members(members_to_exclude, bot)

    async def send_report(self, user_id: UUID, photo_url: str) -> Report:
        report = await self.__report_repository.get_current_report(user_id)
        await self.check_duplicate_report(photo_url)
        report.send_report(photo_url)
        return await self.__report_repository.update(report.id, report)
