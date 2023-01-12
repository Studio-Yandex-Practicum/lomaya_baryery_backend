# TODO: удалить перед мержем в develop

from openpyxl.worksheet.worksheet import Worksheet

from src.excel_generator.base import ExcelBaseGenerator


class ExcelTestGenerator(ExcelBaseGenerator):
    """Тестовый генератор excel отчёта."""

    async def generate_test_report(self) -> Worksheet:
        sheet: Worksheet = self.workbook.create_sheet(self.Sheets.TEST.value)
        sheet.cell(row=1, column=1, value="тест")
        return sheet
