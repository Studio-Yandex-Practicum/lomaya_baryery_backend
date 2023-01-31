from src.excel_generator.builder import AnalyticReportBuilder


class AnalyticTaskReportBuilder(AnalyticReportBuilder):
    """Строитель отчёта для заданий."""

    def __init__(self) -> None:
        super().__init__(
            "Задачи",
            ("Задача", "Кол-во принятых отчётов", "Кол-во отклонённых отчётов", "Кол-во не предоставленных отчётов"),
            ("ИТОГО:", "=SUM(B2:B32)", "=SUM(C2:C32)", "=SUM(D2:D32)"),
        )

    def add_last_row(self) -> None:
        footer_data = [
            "ИТОГО:",
            f"=SUM(B2:B{self.data_count})",
            f"=SUM(C2:C{self.data_count})",
            f"=SUM(D2:D{self.data_count})",
        ]
        if self.data_count > 32:
            self.footer_data = tuple(footer_data)
        super().add_last_row()
