from fastapi import Depends
from fastapi.responses import StreamingResponse

from src.core.services.analytic_report_service import AnalyticReportService


class AnaliticsService:
    """Сервис для получения отчётов."""

    def __init__(self, analytic_report_service: AnalyticReportService = Depends()) -> None:
        self.__analytic_report_service = analytic_report_service

    async def generate_full_report(self) -> StreamingResponse:
        """Генерация полного отчёта."""
        workbook = await self.__analytic_report_service.generate_workbook()
        return await self.__analytic_report_service.generate_full_report(workbook)

    async def generate_task_report(self) -> StreamingResponse:
        """Генерация отчёта с заданиями."""
        workbook = await self.__analytic_report_service.generate_workbook()
        return await self.__analytic_report_service.generate_task_report(workbook)
