from dataclasses import dataclass


@dataclass
class BaseAnalyticReportSettings:
    sheet_name: str
    header_data: tuple[str]
    row_count: int
