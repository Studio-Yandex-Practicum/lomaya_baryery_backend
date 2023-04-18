class BaseAnalyticReportSettings:
    def __init__(self,
                 sheet_name: str,
                 header_data: tuple[tuple[str]],
                 row_count: int):
        self.sheet_name = sheet_name
        self.header_data = header_data
        self.row_coun = row_count


class TaskAnalyticReportSettings(BaseAnalyticReportSettings):
    """Конфигурация отчёта для заданий"""

    sheet_name: str = "Задачи"
    header_data: tuple[str] = (
        "Задача", "Кол-во принятых отчётов", "Кол-во отклонённых отчётов", "Кол-во не предоставленных отчётов"
    )
    row_count: int = 0

    @classmethod
    @property
    def footer_data(self):
        result = (
            "ИТОГО:",
            f"=SUM(B2:B{self.row_count})",
            f"=SUM(C2:C{self.row_count})",
            f"=SUM(D2:D{self.row_count})",
        )
        return result
