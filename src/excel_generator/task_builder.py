from src.excel_generator.base_analytic_report_settings import BaseAnalyticReportSettings


class TaskAnalyticReportSettings(BaseAnalyticReportSettings):
    """Конфигурация отчёта для заданий."""

    sheet_name: str = "Задачи"
    header_data: tuple[str] = (
        "№ Задачи",
        "Название",
        "Кол-во принятых отчётов",
        "Кол-во отклонённых отчётов",
        "Кол-во не предоставленных отчётов",
    )
    row_count: int = 0

    @classmethod
    @property
    def footer_data(cls):
        return (
            "ИТОГО:",
            "",
            f"=SUM(B2:B{cls.row_count})",
            f"=SUM(C2:C{cls.row_count})",
            f"=SUM(D2:D{cls.row_count})",
        )
