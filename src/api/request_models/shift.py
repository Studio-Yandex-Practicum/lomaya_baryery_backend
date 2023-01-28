import enum
import re
from datetime import date

from pydantic import Field, validator

from src.api.request_models.request_base import RequestBase


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
        if not re.match(r'[0-9]{4}-(0[1-9]|1[012])-(0[1-9]|1[0-9]|2[0-9]|3[01])', value):
            raise ValueError('Неверный формат даты. Необходимо указывать дату в формате YYYY-MM-DD.')
        return value


class ShiftUpdateRequest(ShiftCreateRequest):
    final_message: str = Field(..., min_length=10, max_length=400)
