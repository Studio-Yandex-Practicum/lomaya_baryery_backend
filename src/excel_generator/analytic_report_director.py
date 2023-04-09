from typing import Optional

from openpyxl import Workbook

from src.core.db.DTO_models import TasksAnalyticReportDto
from src.excel_generator.builder import AnalyticReportBuilder
from src.excel_generator.task_builder import BaseAnalyticReportSettings


class AnalyticReportDirector:
    """Управляющий отчётами."""

    def __init__(self, builder: AnalyticReportBuilder) -> None:
        self.__builder = builder

    async def generate_report(
        self,
        data: tuple[TasksAnalyticReportDto],
        workbook: Optional[Workbook] = None,
        analytic_task_report_full: Optional[BaseAnalyticReportSettings] = None
    ) -> Workbook:
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
