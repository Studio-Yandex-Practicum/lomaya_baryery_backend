import enum
from datetime import date, datetime

from pydantic import Field, validator

from src.api.request_models.request_base import RequestBase

DATE_FORMAT = "%Y-%m-%d"


class ShiftSortRequest(str, enum.Enum):
    """Поля модели Shift для сортировки."""

    STATUS = "status"
    STARTED_AT = "started_at"
    FINISHED_AT = "finished_at"


class ShiftCreateRequest(RequestBase):
    started_at: date
    finished_at: date
    title: str = Field(..., min_length=3, max_length=60)

    @validator("started_at", "finished_at", pre=True)
    def validate_date_format(cls, value):
        datetime.strptime(value, DATE_FORMAT)
        return value


class ShiftUpdateRequest(ShiftCreateRequest):
    final_message: str = Field(..., min_length=10, max_length=400)
