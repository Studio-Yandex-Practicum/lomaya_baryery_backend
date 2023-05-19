from datetime import date
from io import BytesIO
from urllib.parse import quote_plus
from uuid import UUID

from fastapi import Depends
from openpyxl import Workbook

from src.core.db.models import Shift
from src.core.db.repository.shift_repository import ShiftRepository
from src.core.db.repository.task_repository import TaskRepository
from src.excel_generator.builder import AnalyticReportBuilder
from src.excel_generator.shift_builder import ShiftAnalyticReportSettings
from src.excel_generator.task_builder import TaskAnalyticReportSettings


class AnalyticsService:
    """Сервис для получения отчётов."""

    def __init__(
        self,
        task_repository: TaskRepository = Depends(),
        shift_repository: ShiftRepository = Depends(),
        task_report_builder: AnalyticReportBuilder = Depends(),
    ) -> None:
        self.__task_report_builder = task_report_builder
        self.__task_repository = task_repository
        self.__shift_repository = shift_repository

    @staticmethod
    async def __generate_task_report_description() -> str:
        """Генерация описания к отчёту с заданиями."""
        return f"Отчёт по задачам\nдата формирования отчёта: {date.today().strftime('%d.%m.%Y')}"

    async def __generate_task_report(self, workbook: Workbook) -> None:
        """Генерация отчёта с заданиями."""
        tasks_statistic = await self.__task_repository.get_tasks_statistics_report()
        description = await self.__generate_task_report_description()
        await self.__task_report_builder.generate_report(
            description,
            tasks_statistic,
            workbook=workbook,
            analytic_task_report_full=TaskAnalyticReportSettings,
        )

    async def __generate_shift_report_description(self, shift: Shift) -> str:
        """Генерация описания к отчёту по выбранной смене."""
        return (
            f"Отчёт по смене №{shift.sequence_number} ({shift.title})\n"
            f"дата старта: {shift.started_at.strftime('%d.%m.%Y')}\n"
            f"дата окончания: {shift.finished_at.strftime('%d.%m.%Y')}\n"
            f"дата формирования отчёта: {date.today().strftime('%d.%m.%Y')}"
        )

    async def __generate_report_for_shift(self, workbook: Workbook, shift: Shift) -> None:
        """Генерация отчёта по выбранной смене."""
        shift_statistic = await self.__shift_repository.get_shift_statistics_report_by_id(shift.id)
        description = await self.__generate_shift_report_description(shift)
        await self.__task_report_builder.generate_report(
            description,
            shift_statistic,
            workbook=workbook,
            analytic_task_report_full=ShiftAnalyticReportSettings,
        )

    async def generate_full_report(self) -> BytesIO:
        """Генерация полного отчёта."""
        workbook = self.__task_report_builder.create_workbook()
        await self.__generate_task_report(workbook)
        await self.__generate_task_report(workbook)
        return await self.__task_report_builder.get_report_response(workbook)

    async def generate_task_report(self) -> BytesIO:
        """Генерация отчёта с заданиями."""
        workbook = self.__task_report_builder.create_workbook()
        await self.__generate_task_report(workbook)
        return await self.__task_report_builder.get_report_response(workbook)

    async def generate_report_for_shift(self, shift: Shift) -> BytesIO:
        """Генерация отчёта по выбранной смене."""
        workbook = self.__task_report_builder.create_workbook()
        await self.__generate_report_for_shift(workbook, shift)
        return await self.__task_report_builder.get_report_response(workbook)

    async def generate_shift_report_filename(self, shift_id: UUID) -> tuple[str | Shift]:
        """Генерация названия файла отчета по смене."""
        shift = await self.__shift_repository.get(shift_id)
        shift_name = shift.title.replace(' ', '_').replace('.', '')
        filename = f"Отчёт_по_смене_№{shift.sequence_number}_{shift_name}_{date.today().strftime('%d-%m-%Y')}.xlsx"
        return quote_plus(filename), shift
