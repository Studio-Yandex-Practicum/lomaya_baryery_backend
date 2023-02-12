from typing import Optional

from fastapi import Depends
from fastapi.responses import StreamingResponse
from openpyxl import Workbook

from src.core.db.repository.task_repository import TaskRepository
from src.excel_generator.analytic_report_director import AnalyticReportDirector
from src.excel_generator.task_builder import AnalyticTaskReportBuilder


class AnalyticsService:
    """Сервис для получения отчётов."""

    def __init__(self, task_repository: TaskRepository = Depends()) -> None:
        self.__task_repository = task_repository
        self.__task_report_builder = AnalyticTaskReportBuilder()

    async def __generate_task_report(self, last_sheet: bool, workbook: Optional[Workbook] = None) -> Workbook:
        """Генерация отчёта с заданиями."""
        tasks_statistic = await self.__task_repository.get_tasks_statistics_report()
        return await AnalyticReportDirector(self.__task_report_builder).generate_report(
            tasks_statistic, last_sheet, workbook
        )

    async def generate_full_report(self) -> StreamingResponse:
        """Генерация полного отчёта."""
        workbook = await self.__generate_task_report(last_sheet=True)
        # Ниже пример использование флага при добавлении новых отчётов:
        # workbook = await self.__generate_task_report(last_sheet=False)
        # workbook = await self.__generate_shift_report(workbook=workbook, last_sheet=True)
        return workbook  # noqa: R504

    async def generate_task_report(self) -> StreamingResponse:
        """Генерация отчёта с заданиями."""
        return await self.__generate_task_report(last_sheet=True)
