from dataclasses import astuple

from openpyxl.worksheet.worksheet import Worksheet

from src.core.db.DTO_models import TasksExcelReportDto
from src.excel_generator.base import ExcelBaseGenerator


class ExcelTasksGenerator(ExcelBaseGenerator):
    """Генератор excel отчёта по задачач."""

    async def generate_tasks_statistics_report(self, data: tuple[TasksExcelReportDto]) -> Worksheet:

        sheet: Worksheet = self.workbook.create_sheet(self.Sheets.TASKS.value)

        # создаём хэдер отчёта
        header_data = (
            "Задача",
            "Кол-во принятых отчётов",
            "Кол-во отклонённых отчётов",
            "Кол-во не предоставленных отчётов",
        )
        self.fill_row(sheet, header_data, 1)

        # заполняем отчёт данными
        for idx, task in enumerate(data):
            row_num = idx + 2
            self.fill_row(sheet, astuple(task), row_num)

        # создаём футер отчёта
        footer_data = (
            "ИТОГО:",
            "=SUM(B2, B32)",
            "=SUM(C2, C32)",
            "=SUM(D2, D32)",
        )
        self.fill_row(sheet, footer_data, 33)

        # задаём стили
        self.make_styling(sheet, 33)

        return sheet
