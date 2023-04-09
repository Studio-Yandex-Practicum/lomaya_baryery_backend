from typing import Optional

from fastapi import Depends
from fastapi.responses import StreamingResponse
from openpyxl import Workbook

from src.core.db.repository.task_repository import TaskRepository
from src.excel_generator.analytic_report_director import AnalyticReportDirector
from src.core.db.DTO_models import TasksAnalyticReportDto
from src.excel_generator.builder import AnalyticReportBuilder
from src.excel_generator.task_builder import TaskAnalyticReportSettings


class AnalyticsService:
    """Сервис для получения отчётов."""

    def __init__(self, task_repository: TaskRepository = Depends()) -> None:
        self.__task_repository = task_repository
        self.__task_report_builder = AnalyticReportBuilder()
        self._analytic_report_builder = AnalyticReportBuilder()

    async def __generate_task_report(self,
                                     tasks_statistic: tuple[TasksAnalyticReportDto],
                                     workbook: Optional[Workbook] = None) -> Workbook:
        """Генерация отчёта с заданиями."""
        return await AnalyticReportDirector(self.__task_report_builder).generate_report(
            data=tasks_statistic, workbook=workbook,
            analytic_task_report_full=TaskAnalyticReportSettings
        )

    async def generate_full_report(self) -> StreamingResponse:
        """Генерация полного отчёта."""
        workbook = self.__task_report_builder.create_workbook()
        tasks_statistic = await self.__task_repository.get_tasks_statistics_report()
        # data = await добавляем какие-то другие данные из базы 
        workbook = await self.__generate_task_report(tasks_statistic=tasks_statistic, workbook=workbook)
        # await self.__generate_task_report(tasks_statistic=data, workbook=workbook)
        # Создаёт новый лист в отчёте
        workbook = await self._analytic_report_builder.get_report_response(workbook=workbook)
        return workbook

    async def generate_task_report(self) -> StreamingResponse:
        """Генерация отчёта с заданиями."""
        workbook = self.__task_report_builder.create_workbook()
        tasks_statistic = await self.__task_repository.get_tasks_statistics_report()
        workbook = await self.__generate_task_report(tasks_statistic=tasks_statistic, workbook=workbook)
        workbook = await self._analytic_report_builder.get_report_response(workbook=workbook)
        return workbook
