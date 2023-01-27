from fastapi import Depends
from fastapi.responses import StreamingResponse

from src.core.services.excel_report_service import ExcelReportService
from src.excel_generator.tasks_excel_generator import ExcelTasksGenerator


class AnaliticsService:
    def __init__(
        self,
        excel_report_service: ExcelReportService = Depends(),
        tasks_excel_generator: ExcelTasksGenerator = Depends(),
    ) -> None:
        self.__excel_report_service = excel_report_service
        self.__tasks_excel_generator = tasks_excel_generator

    async def generate_full_report(self) -> StreamingResponse:
        """Полный репорт."""
        reports = (self.__tasks_excel_generator.sheet_name,)
        return await self.__excel_report_service.generate_report(reports)

    async def generate_tasks_report(self) -> StreamingResponse:
        """Репорт с задачами со всех смен."""
        return await self.__excel_report_service.generate_report((self.__tasks_excel_generator.sheet_name,))
