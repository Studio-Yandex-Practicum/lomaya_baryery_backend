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
