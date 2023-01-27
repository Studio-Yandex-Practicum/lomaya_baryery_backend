from dataclasses import astuple

from fastapi import Depends
from openpyxl.worksheet.worksheet import Worksheet

from src.core.db.DTO_models import TasksExcelReportDto
from src.excel_generator.base import ExcelBaseGenerator


class ExcelTasksGenerator:
    """Генератор excel отчёта по задачам."""

    def __init__(self, base_generator: ExcelBaseGenerator = Depends()):
        self.__base_generator = base_generator
        self.sheet_name = "Задачи"

    async def generate_tasks_statistics_report(self, data: tuple[TasksExcelReportDto]) -> Worksheet:
        sheet = self.__base_generator.create_sheet(self.sheet_name)
        total_tasks = len(data)
        header_data = (
            "Задача",
            "Кол-во принятых отчётов",
            "Кол-во отклонённых отчётов",
            "Кол-во не предоставленных отчётов",
        )
        self.__base_generator.fill_row(sheet, header_data, 1)
        for idx, task in enumerate(data):
            row_num = idx + 2
            self.__base_generator.fill_row(sheet, astuple(task), row_num)
        footer_data = (
            "ИТОГО:",
            f"=SUM(B2, B{total_tasks})",
            f"=SUM(C2, C{total_tasks})",
            f"=SUM(D2, D{total_tasks})",
        )
        self.__base_generator.fill_row(sheet, footer_data, total_tasks + 1)
        self.__base_generator.make_styling(sheet, total_tasks + 1)
        return sheet
