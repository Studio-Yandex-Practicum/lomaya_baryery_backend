import abc
import enum
from dataclasses import astuple

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.worksheet.worksheet import Worksheet


class AnalyticReportBuilder(abc.ABC):
    """Интерфейс строителя."""

    def __init__(self, sheet_name: str, header_data: tuple[str], footer_data: tuple[str]) -> None:
        self.sheet_name = sheet_name
        self.header_data = header_data
        self.footer_data = footer_data
        self.sheet: Worksheet | None = None
        self.data_count: int = 0

    def __set_data_count(self, data_list: tuple[str]) -> None:
        self.data_count = len(data_list)

    def __add_row(self, data_list: tuple[str], row_number: int) -> None:
        for index, value in enumerate(data_list):
            self.sheet.cell(row=row_number, column=index + 1, value=value)

    def create_sheet(self, workbook: Workbook) -> None:
        """Создаёт лист внутри отчёта."""
        self.sheet = workbook.create_sheet(self.sheet_name)

    def add_first_row(self) -> None:
        """Заполняет первую строку в листе."""
        self.__add_row(self.header_data, 1)

    def add_data_row(self, data_list: tuple[str]) -> None:
        """Заполняет строку данными из БД."""
        self.__set_data_count(data_list)
        for index, task in enumerate(data_list):
            row_number = index + 2
            self.__add_row(astuple(task), row_number)

    def add_last_row(self) -> None:
        """Заполняет последнюю строку в листе."""
        self.__add_row(self.footer_data, self.data_count + 2)

    def make_styling(self):
        """Задаёт форматирование отчёта."""
        max_row = self.data_count + 2
        # задаём стиль для хэдера
        header_cells = list(self.sheet.iter_rows())[0]
        for cell in header_cells:
            cell.font = self.Styles.FONT_BOLD.value
            cell.alignment = self.Styles.ALIGNMENT_HEADER.value
        # задаём стиль для ячеек с данными
        data_rows = list(self.sheet.iter_rows())[1:max_row - 1]  # fmt: skip
        for row in data_rows:
            for cell in row:
                cell.font = self.Styles.FONT_STANDART.value
                cell.alignment = self.Styles.ALIGNMENT_STANDART.value
        # задаём стиль для футера
        footer_cells = list(self.sheet.iter_rows())[max_row - 1]
        for cell in footer_cells:
            cell.font = self.Styles.FONT_BOLD.value
            cell.alignment = self.Styles.ALIGNMENT_STANDART.value
        # задаём стиль границ и колонок
        for row in self.sheet.iter_rows():
            for cell in row:
                cell.border = self.Styles.BORDER.value
        self.sheet.column_dimensions["A"].width = self.Styles.WIDTH.value

    class Styles(enum.Enum):
        FONT_BOLD = Font(name='Times New Roman', size=11, bold=True)
        FONT_STANDART = Font(name='Times New Roman', size=11, bold=False)
        ALIGNMENT_HEADER = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ALIGNMENT_STANDART = Alignment(horizontal='left', vertical='center', wrap_text=True)
        BORDER = Border(
            left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin')
        )
        WIDTH = 50
