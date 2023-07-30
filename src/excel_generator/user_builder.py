from dataclasses import dataclass, field

from src.excel_generator.base_analytic_report_settings import BaseAnalyticReportSettings


class UserTaskAnalyticReportSettings(BaseAnalyticReportSettings):
    """Конфигурация отчёта участника в разрезе задач."""

    sheet_name: str = "Отчёт по задачам участника"
    header_data: tuple[str] = (
        "№ Задачи",
        "Название задачи",
        "Принята с 1-й попытки",
        "Принята с 2-й попытки",
        "Принята с 3-й попытки",
        "Кол-во одобренных отчётов",
        "Кол-во отклонённых отчётов",
        "Кол-во пропущенных заданий",
        "Всего отчётов",
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


@dataclass
class UserShiftAnalyticReportSettings:
    """Конфигурация отчёта участника в разрезе смен."""

    sheet_name: str = "Отчёт по сменам участника"
    header_data: tuple[str] = (
        "№ Смены",
        "Название смены",
        "Принята с 1-й попытки",
        "Принята с 2-й попытки",
        "Принята с 3-й попытки",
        "Кол-во одобренных отчётов",
        "Кол-во отклонённых отчётов",
        "Кол-во пропущенных заданий",
        "Всего отчётов",
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


@dataclass
class UserFullAnalyticReportSettings:
    sheet_name: str = "Полный отчёт"
    shifts: list[str | None] = field(default_factory=lambda: [])
    header_data: list[str] = field(default_factory=lambda: ["№", "Название задачи"])
    row_count: int = 0

    def add_shift(self, shift_name: str):
        statistics_column_names = ["1п", "2п", "3п", "Од", "От", "Пр", "Вс"]
        self.shifts.append(shift_name)
        self.header_data.extend(statistics_column_names)

    def add_summary_column(self):
        ...

    @staticmethod
    def _make_column_name(index: int):
        """Вычисляет имя колонки excel по индексу.

        Имя колонки в excel — это последовательность A, B, ... Z, AA, AB, ... ZZ, AAA, AAB

        """
        a = ord("A")
        z = ord("Z")

        q, third_index = divmod(index, z - a + 1)
        first_index, second_index = divmod(q, z - a + 1)

        first_letter = chr(a - 1 + first_index) if first_index else ""
        second_letter = chr(a - 1 + second_index) if second_index else ""
        third_letter = chr(a + third_index)

        return "".join([first_letter, second_letter, third_letter])

    @property
    def footer_data(self):
        first_row_for_calculation = 3  # номер строки, где  начинаются данные
        result = ["ИТОГО:", ""]
        formulae = "=SUM({column}{start_row}:{column}{end_row})"

        for index in range(len(result), len(self.header_data)):
            column = self._make_column_name(index)
            result.append(formulae.format(column=column, start_row=first_row_for_calculation, end_row=self.row_count))

        return result
