from src.excel_generator.task_builder import BaseAnalyticReportSettings


class ShiftAnalyticReportSettings(BaseAnalyticReportSettings):
    """Конфигурация отчёта для текущей смены."""

    sheet_name: str = "Текущая смена"
    header_data: tuple[str] = (
        "Задача",
        "Принята с 1-й попытки",
        "Принята с 2-й попытки",
        "Принята с 3-й попытки",
        "Кол-во пропусков задания",
        "Кол-во одобренных отчётов",
        "Кол-во отклонённых отчётов",
    )
    row_count: int = 0

    @classmethod
    @property
    def footer_data(cls):
        return (
            "ИТОГО:",
            f"=SUM(B2:B{cls.row_count})",
            f"=SUM(C2:C{cls.row_count})",
            f"=SUM(D2:D{cls.row_count})",
            f"=SUM(E2:E{cls.row_count})",
            f"=SUM(F2:F{cls.row_count})",
            f"=SUM(G2:G{cls.row_count})",
        )
