import weakref
from src.core.db.DTO_models import AnalyticTaskReportSheetDTO


class classproperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class AnalyticTaskReportFull(AnalyticTaskReportSheetDTO):
    """Строитель отчёта для заданий"""
    def __init__(self):
        self.footer_data.append(weakref.ref(self))

    sheet_name: str = "Задачи"
    header_data: tuple[tuple[str]] = (
        ("Задача", "Кол-во принятых отчётов", "Кол-во отклонённых отчётов", "Кол-во не предоставленных отчётов"),
    )
    row_count: int = 0

    @classproperty
    def footer_data(self):
        result = [
            "ИТОГО:",
            f"=SUM(B2:B{self.row_count})",
            f"=SUM(C2:C{self.row_count})",
            f"=SUM(D2:D{self.row_count})",
        ]
        result = tuple(result)
        return result
