from typing import Optional

from fastapi.responses import StreamingResponse
from openpyxl import Workbook

from src.excel_generator.builder import AnalyticReportBuilder


class AnalyticReportDirector:
    """Управляющий отчётами."""

    def __init__(self, builder: AnalyticReportBuilder) -> None:
        self.__builder = builder

    async def generate_report(
        self, data: tuple, last_sheet: bool, workbook: Optional[Workbook] = None
    ) -> Workbook | StreamingResponse:
        """Генерация листа с данными."""
        workbook = await self.__builder.create_workbook() if not workbook else workbook
        self.__builder.create_sheet(workbook)
        self.__builder.add_header()
        self.__builder.add_data(data)
        self.__builder.add_footer()
        self.__builder.apply_styles()
        if last_sheet:
            return await self.__builder.get_report_response(workbook)
        return workbook
