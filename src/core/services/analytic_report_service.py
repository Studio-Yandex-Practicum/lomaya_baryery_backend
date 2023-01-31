from datetime import datetime
from io import BytesIO

from fastapi import Depends
from fastapi.responses import StreamingResponse
from openpyxl import Workbook

from src.core.db.repository.task_repository import TaskRepository
from src.excel_generator import AnalyticReportDirector
from src.excel_generator.task_builder import AnalyticTaskReportBuilder


class AnalyticReportService:
    """Сервис для создания отчётов."""

    def __init__(self, task_repository: TaskRepository = Depends()) -> None:
        self.__task_repository = task_repository

    async def __generate_task_report(self, workbook: Workbook) -> Workbook:
        """Генерация отчёта с заданиями."""
        data = await self.__task_repository.get_tasks_statistics_report()
        builder = AnalyticTaskReportBuilder()
        return await AnalyticReportDirector(builder).generate_report(data, workbook)

    async def __save_report(self, workbook: Workbook) -> BytesIO:
        """Сохранение отчёта."""
        stream = BytesIO()
        workbook.save(stream)
        stream.seek(0)
        return stream

    async def __get_report_response(self, workbook: Workbook) -> StreamingResponse:
        """Создание ответа."""
        stream = await self.__save_report(workbook)
        filename = f"report_{datetime.now()}.xlsx"
        headers = {'Content-Disposition': f'attachment; filename={filename}'}
        return StreamingResponse(stream, headers=headers)

    async def generate_workbook(self) -> Workbook:
        """Генерация excel файла."""
        workbook = Workbook()
        workbook.remove_sheet(workbook.active)
        return workbook

    async def generate_full_report(self, workbook) -> StreamingResponse:
        """Генерация полного отчёта."""
        workbook = await self.__generate_task_report(workbook)
        return await self.__get_report_response(workbook)

    async def generate_task_report(self, workbook) -> StreamingResponse:
        """Генерация отчёта с заданиями."""
        workbook = await self.__generate_task_report(workbook)
        return await self.__get_report_response(workbook)
