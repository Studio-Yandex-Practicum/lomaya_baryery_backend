from openpyxl import Workbook

from src.excel_generator.builder import AnalyticReportBuilder


class AnalyticReportDirector:
    """Управляющий отчётами."""

    def __init__(self, builder: AnalyticReportBuilder) -> None:
        self.__builder = builder

    async def generate_report(self, data: tuple, workbook: Workbook) -> Workbook:
        """Генерация листа с данными."""
        self.__builder.create_sheet(workbook)
        self.__builder.add_first_row()
        self.__builder.add_data_row(data)
        self.__builder.add_last_row()
        self.__builder.make_styling()
        return workbook
