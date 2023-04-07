import os
from typing import Optional

from fastapi import Depends
from fastapi.responses import StreamingResponse
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from src.core.db.repository.task_repository import TaskRepository
from src.excel_generator.analytic_report_director import AnalyticReportDirector
from src.core.db.DTO_models import TasksAnalyticReportDto
from src.excel_generator.builder import AnalyticReportBuilder
from src.excel_generator.task_builder import AnalyticTaskReportFull
from src.core.settings import WORKBOOK_FULL_DIR, FILE_NAME

FILE_PATH = WORKBOOK_FULL_DIR / FILE_NAME


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
            analytic_task_report_full=AnalyticTaskReportFull, worksheet=Worksheet
        )

    async def generate_full_report(self) -> StreamingResponse:
        """Генерация полного отчёта."""
        workbook = load_workbook(FILE_PATH)
        workbook = await self._analytic_report_builder.get_report_response(workbook=workbook)
        return workbook

    async def generate_task_report(self) -> StreamingResponse:
        """Генерация отчёта с заданиями."""
        workbook = self.__task_report_builder.create_workbook()
        tasks = await self.__task_repository.get_tasks_statistics_report()
        workbook = await self.__generate_task_report(tasks_statistic=tasks, workbook=workbook)
        if os.path.exists(FILE_PATH) is False:
            WORKBOOK_FULL_DIR.mkdir(exist_ok=True)
            workbook.save(FILE_PATH)
        else:
            workbook_full = load_workbook(FILE_PATH)
            workbook_full = await self.__generate_task_report(tasks_statistic=tasks, workbook=workbook_full)
            workbook_full.save(FILE_PATH)
        workbook = await self._analytic_report_builder.get_report_response(workbook=workbook)
        return workbook
