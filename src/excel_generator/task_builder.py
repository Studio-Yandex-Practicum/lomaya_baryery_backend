from typing import Optional


class classproperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class BaseAnalyticReportSettings:
    def __init__(self,
                 sheet_name: str,
                 header_data: tuple[tuple[str]],
                 footer_data: Optional[tuple[str]] = None,
                 row_count: Optional[int] = None):
        self.sheet_name = sheet_name
        self.header_data = header_data
        self.footer_data = footer_data
        self.row_coun = row_count


class TaskAnalyticReportSettings(BaseAnalyticReportSettings):
    """Строитель отчёта для заданий"""

    sheet_name: str = "Задачи"
    header_data: tuple[tuple[str]] = (
        ("Задача", "Кол-во принятых отчётов", "Кол-во отклонённых отчётов", "Кол-во не предоставленных отчётов"),
    )
    row_count: int = 0

    @classproperty
    def footer_data(self):
        result = (
            "ИТОГО:",
            f"=SUM(B2:B{self.row_count})",
            f"=SUM(C2:C{self.row_count})",
            f"=SUM(D2:D{self.row_count})",
        )
        return result
