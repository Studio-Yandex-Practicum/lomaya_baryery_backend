from fastapi import Depends
from fastapi.responses import StreamingResponse
from openpyxl import Workbook

from src.core.db.repository.task_repository import TaskRepository
from src.excel_generator.builder import AnalyticReportBuilder
from src.excel_generator.task_builder import TaskAnalyticReportSettings


class AnalyticsService:
    """Сервис для получения отчётов."""

    def __init__(self,
                 task_repository: TaskRepository = Depends()) -> None:
        self.__task_report_builder = AnalyticReportBuilder()
        self.__task_repository = task_repository

    async def __generate_task_report(self,
                                     workbook: Workbook) -> Workbook:
        """Генерация отчёта с заданиями."""
        tasks_statistic = await self.__task_repository.get_tasks_statistics_report()
        return await self.__task_report_builder.generate_report(
            data=tasks_statistic, workbook=workbook,
            analytic_task_report_full=TaskAnalyticReportSettings
        )

    async def __generate_full_report(self,
                                     workbook: Workbook) -> Workbook:
        """Генерация полного отчёта."""
        workbook = await self.__generate_task_report(workbook=workbook)
        workbook = await self.__generate_task_report(workbook=workbook)
        return workbook

    async def generate_full_report(self) -> StreamingResponse:
        """Генерация полного отчёта."""
        workbook = self.__task_report_builder._create_workbook()
        workbook = await self.__generate_full_report(workbook=workbook)
        stream = await self.__task_report_builder._get_report_response(workbook=workbook)
        return stream

    async def generate_task_report(self) -> StreamingResponse:
        """Генерация отчёта с заданиями."""
        workbook = self.__task_report_builder._create_workbook()
        workbook = await self.__generate_task_report(workbook=workbook)
        stream = await self.__task_report_builder._get_report_response(workbook=workbook)
        return stream
