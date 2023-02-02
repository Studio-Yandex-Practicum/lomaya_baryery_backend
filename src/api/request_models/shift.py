import enum
from datetime import date

from pydantic import Field

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


class ShiftUpdateRequest(ShiftCreateRequest):
    final_message: str = Field(..., min_length=10, max_length=400)


class ShiftCancelRequest(RequestBase):
    message: str = Field(..., min_length=10, max_length=400)
