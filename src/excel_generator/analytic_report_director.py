from typing import Optional

from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from src.core.db.DTO_models import TasksAnalyticReportDto
from src.excel_generator.builder import AnalyticReportBuilder
from src.excel_generator.task_builder import AnalyticTaskReportFull


class AnalyticReportDirector:
    """Управляющий отчётами."""

    def __init__(self, builder: AnalyticReportBuilder) -> None:
        self.__builder = builder

    async def generate_report(
        self, data: tuple[TasksAnalyticReportDto],
        workbook: Optional[Workbook] = None,
        worksheet: Optional[Worksheet] = None,
        analytic_task_report_full: Optional[AnalyticTaskReportFull] = None
    ) -> Workbook | StreamingResponse:
        """Генерация листа с данными."""
        worksheet = self.__builder.create_sheet(
            workbook,
            sheet_name=analytic_task_report_full.sheet_name
        )
        analytic_task_report_full.row_count = 0
        self.__builder.add_header(analytic_task_report=analytic_task_report_full, worksheet=worksheet)
        self.__builder.add_data(data, analytic_task_report=analytic_task_report_full, worksheet=worksheet)
        self.__builder.add_footer(analytic_task_report=analytic_task_report_full, worksheet=worksheet)
        self.__builder.apply_styles(worksheet=worksheet)
        return workbook
