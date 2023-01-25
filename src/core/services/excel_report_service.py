from datetime import datetime

from fastapi import Depends
from fastapi.responses import StreamingResponse

from src.core.db.repository.task_repository import TaskRepository
from src.excel_generator.main import excel_generator


class ExcelReportService:
    """Сервис для создания excel отчётов."""

    def __init__(self, task_repository: TaskRepository = Depends()) -> None:
        self.__task_repository = task_repository

    async def __generate_tasks_statistics_report(self) -> None:
        report_data = await self.__task_repository.get_tasks_statistics_report()
        await excel_generator.generate_tasks_statistics_report(report_data)

    async def __get_excel_report_response(self) -> StreamingResponse:
        """Создаёт ответ."""
        stream = await excel_generator.save_report_to_stream()
        filename = f"report_{datetime.now()}.xlsx"
        headers = {'Content-Disposition': f'attachment; filename={filename}'}
        return StreamingResponse(stream, headers=headers)

    async def generate_report(self, reports: tuple[str]) -> StreamingResponse:
        if excel_generator.Sheets.TASKS.value in reports:
            await self.__generate_tasks_statistics_report()
        return await self.__get_excel_report_response()
