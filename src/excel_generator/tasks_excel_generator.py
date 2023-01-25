from dataclasses import astuple

from openpyxl.worksheet.worksheet import Worksheet

from src.core.db.DTO_models import TasksExcelReportDto
from src.excel_generator.base import ExcelBaseGenerator


class ExcelTasksGenerator(ExcelBaseGenerator):
    """Генератор excel отчёта по задачам."""

    async def generate_tasks_statistics_report(self, data: tuple[TasksExcelReportDto]) -> Worksheet:
        sheet: Worksheet = self.workbook.create_sheet(self.Sheets.TASKS.value)
        total = len(data)
        header_data = (
            "Задача",
            "Кол-во принятых отчётов",
            "Кол-во отклонённых отчётов",
            "Кол-во не предоставленных отчётов",
        )
        self.fill_row(sheet, header_data, 1)
        for idx, task in enumerate(data):
            row_num = idx + 2
            self.fill_row(sheet, astuple(task), row_num)
        footer_data = (
            "ИТОГО:",
            f"=SUM(B2, B{total})",
            f"=SUM(C2, C{total})",
            f"=SUM(D2, D{total})",
        )
        self.fill_row(sheet, footer_data, total + 1)
        self.make_styling(sheet, total + 1)
        return sheet
