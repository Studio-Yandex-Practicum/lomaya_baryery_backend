from datetime import datetime

from fastapi import Depends
from fastapi.responses import StreamingResponse

from src.core.db.repository.task_repository import TaskRepository
from src.excel_generator.base import ExcelBaseGenerator
from src.excel_generator.tasks_excel_generator import ExcelTasksGenerator


class ExcelReportService:
    """Сервис для создания excel отчётов."""

    def __init__(
        self,
        base_generator: ExcelBaseGenerator = Depends(),
        task_repository: TaskRepository = Depends(),
        tasks_excel_generator: ExcelTasksGenerator = Depends(),
    ) -> None:
        self.__base_generator = base_generator
        self.__task_repository = task_repository
        self.__tasks_excel_generator = tasks_excel_generator

    async def __generate_tasks_statistics_report(self) -> None:
        report_data = await self.__task_repository.get_tasks_statistics_report()
        await self.__tasks_excel_generator.generate_tasks_statistics_report(report_data)

    async def __get_excel_report_response(self) -> StreamingResponse:
        """Создаёт ответ."""
        stream = await self.__base_generator.save_report_to_stream()
        filename = f"report_{datetime.now()}.xlsx"
        headers = {'Content-Disposition': f'attachment; filename={filename}'}
        return StreamingResponse(stream, headers=headers)

    async def generate_report(self, reports: tuple[str]) -> StreamingResponse:
        if self.__tasks_excel_generator.sheet_name in reports:
            await self.__generate_tasks_statistics_report()
        return await self.__get_excel_report_response()
