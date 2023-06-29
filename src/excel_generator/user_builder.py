from src.excel_generator.base_analytic_report_settings import BaseAnalyticReportSettings


class UserTaskAnalyticReportSettings(BaseAnalyticReportSettings):
    """Конфигурация отчёта участника в разрезе задач."""

    sheet_name: str = "Отчёт по задачам участника"
    header_data: tuple[str] = (
        "№ Задачи",
        "Название задачи",
        "1",
        "2",
        "3",
        "П",
        "Д",
        "О",
        "В",
    )
    row_count: int = 0

    @classmethod
    @property
    def footer_data(cls):
        return (
            "ИТОГО:",
            "",
            f"=SUM(C2:C{cls.row_count})",
            f"=SUM(D2:D{cls.row_count})",
            f"=SUM(E2:E{cls.row_count})",
            f"=SUM(F2:F{cls.row_count})",
            f"=SUM(G2:G{cls.row_count})",
            f"=SUM(H2:H{cls.row_count})",
            f"=SUM(I2:I{cls.row_count})",
        )


class UserShiftAnalyticReportSettings(BaseAnalyticReportSettings):
    """Конфигурация отчёта участника в разрезе смен."""

    sheet_name: str = "Отчёт по сменам участника"
    header_data: tuple[str] = (
        "№ Смены",
        "Название смены",
        "1",
        "2",
        "3",
        "П",
        "Д",
        "О",
        "В",
    )
    row_count: int = 0

    @classmethod
    @property
    def footer_data(cls):
        return (
            "ИТОГО:",
            "",
            f"=SUM(C2:C{cls.row_count})",
            f"=SUM(D2:D{cls.row_count})",
            f"=SUM(E2:E{cls.row_count})",
            f"=SUM(F2:F{cls.row_count})",
            f"=SUM(G2:G{cls.row_count})",
            f"=SUM(H2:H{cls.row_count})",
            f"=SUM(I2:I{cls.row_count})",
        )
