import abc
import enum
from dataclasses import astuple
from datetime import datetime
from io import BytesIO

from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, Side


class AnalyticReportBuilder(abc.ABC):
    """Интерфейс строителя."""

    def __set_data_count(self, data: tuple[str]) -> None:
        self._data_count = len(data)

    def __add_row(self, data: tuple[str], row_number: int) -> None:
        for index, value in enumerate(data):
            self._worksheet.cell(row=row_number, column=index + 1, value=value)

    async def __save_report(self, workbook: Workbook) -> BytesIO:
        """Сохранение отчёта."""
        stream = BytesIO()
        workbook.save(stream)
        stream.seek(0)
        return stream

    async def get_report_response(self, workbook: Workbook) -> StreamingResponse:
        """Создание ответа."""
        stream = await self.__save_report(workbook)
        filename = f"report_{datetime.now()}.xlsx"
        headers = {'Content-Disposition': f'attachment; filename={filename}'}
        return StreamingResponse(stream, headers=headers)

    async def create_workbook(self) -> Workbook:
        """Генерация excel файла."""
        workbook = Workbook()
        workbook.remove_sheet(workbook.active)
        return workbook

    def create_sheet(self, workbook: Workbook) -> None:
        """Создаёт лист внутри отчёта."""
        self._worksheet = workbook.create_sheet(self._sheet_name)

    def add_header(self) -> None:
        """Заполняет первую строку в листе."""
        self.__add_row(self._header_data, 1)

    def add_data(self, data: tuple[str]) -> None:
        """Заполняет строку данными из БД."""
        self.__set_data_count(data)
        for index, task in enumerate(data):
            row_number = index + 2
            self.__add_row(astuple(task), row_number)

    def add_footer(self) -> None:
        """Заполняет последнюю строку в листе."""
        self.__add_row(self._footer_data, self._data_count + 2)

    def apply_styles(self):
        """Задаёт форматирование отчёта."""
        max_row = self._data_count + 2
        # задаём стиль для хэдера
        header_cells = list(self._worksheet.iter_rows())[0]
        for cell in header_cells:
            cell.font = self.Styles.FONT_BOLD.value
            cell.alignment = self.Styles.ALIGNMENT_HEADER.value
        # задаём стиль для ячеек с данными
        data_rows = list(self._worksheet.iter_rows())[1:max_row - 1]  # fmt: skip
        for row in data_rows:
            for cell in row:
                cell.font = self.Styles.FONT_STANDART.value
                cell.alignment = self.Styles.ALIGNMENT_STANDART.value
        # задаём стиль для футера
        footer_cells = list(self._worksheet.iter_rows())[max_row - 1]
        for cell in footer_cells:
            cell.font = self.Styles.FONT_BOLD.value
            cell.alignment = self.Styles.ALIGNMENT_STANDART.value
        # задаём стиль границ и колонок
        for row in self._worksheet.iter_rows():
            for cell in row:
                cell.border = self.Styles.BORDER.value
        self._worksheet.column_dimensions["A"].width = self.Styles.WIDTH.value

    class Styles(enum.Enum):
        FONT_BOLD = Font(name='Times New Roman', size=11, bold=True)
        FONT_STANDART = Font(name='Times New Roman', size=11, bold=False)
        ALIGNMENT_HEADER = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ALIGNMENT_STANDART = Alignment(horizontal='left', vertical='center', wrap_text=True)
        BORDER = Border(
            left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin')
        )
        WIDTH = 50
