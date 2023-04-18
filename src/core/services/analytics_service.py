from fastapi import Depends
from fastapi.responses import StreamingResponse
from openpyxl import Workbook

from src.core.db.repository.task_repository import TaskRepository
from src.excel_generator.builder import AnalyticReportBuilder
from src.excel_generator.task_builder import TaskAnalyticReportSettings


class AnalyticsService:
    """Сервис для получения отчётов."""

    def __init__(self,
                 task_repository: TaskRepository = Depends(),
                 task_report_builder: AnalyticReportBuilder = Depends()) -> None:
        self.__task_report_builder = task_report_builder
        self.__task_repository = task_repository

    async def __generate_task_report(self,
                                     workbook: Workbook) -> Workbook:
        """Генерация отчёта с заданиями."""
        tasks_statistic = await self.__task_repository.get_tasks_statistics_report()
        await self.__task_report_builder.generate_report(
            tasks_statistic, workbook=workbook,
            analytic_task_report_full=TaskAnalyticReportSettings
        )

    async def __generate_full_report(self,
                                     workbook: Workbook) -> Workbook:
        """Генерация полного отчёта."""
        await self.__generate_task_report(workbook)
        await self.__generate_task_report(workbook)

    async def generate_full_report(self) -> StreamingResponse:
        """Генерация полного отчёта."""
        workbook = self.__task_report_builder.create_workbook()
        await self.__generate_full_report(workbook)
        stream = await self.__task_report_builder.get_report_response(workbook)
        return stream

    async def generate_task_report(self) -> StreamingResponse:
        """Генерация отчёта с заданиями."""
        workbook = self.__task_report_builder.create_workbook()
        await self.__generate_task_report(workbook)
        stream = await self.__task_report_builder.get_report_response(workbook)
        return stream
