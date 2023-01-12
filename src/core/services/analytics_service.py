from fastapi import Depends
from fastapi.responses import StreamingResponse

from src.core.services.excel_report_service import ExcelReportService
from src.excel_generator.base import ExcelBaseGenerator


class AnaliticsService:
    def __init__(self, excel_report_service: ExcelReportService = Depends()) -> None:
        self.__excel_report_service = excel_report_service

    async def generate_report(self) -> StreamingResponse:
        reports = tuple(report.value for report in ExcelBaseGenerator.Sheets)
        return await self.__excel_report_service.generate_report(reports)
