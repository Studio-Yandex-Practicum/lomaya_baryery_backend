from typing import Optional

from openpyxl.worksheet.worksheet import Worksheet

from src.excel_generator.builder import AnalyticReportBuilder


class AnalyticTaskReportBuilder(AnalyticReportBuilder):
    """Строитель отчёта для заданий."""

    def __init__(self) -> None:
        self._sheet_name: str = "Задачи"
        self._header_data: tuple[tuple[str]] = (
            ("Задача", "Кол-во принятых отчётов", "Кол-во отклонённых отчётов", "Кол-во не предоставленных отчётов"),
        )
        self._footer_data: Optional[tuple[str]] = None
        self._worksheet: Optional[Worksheet] = None
        self._row_count: int = 0

    def add_footer(self) -> None:
        footer_data = [
            "ИТОГО:",
            f"=SUM(B2:B{self._row_count})",
            f"=SUM(C2:C{self._row_count})",
            f"=SUM(D2:D{self._row_count})",
        ]
        self._footer_data = tuple(footer_data)
        return super().add_footer()
