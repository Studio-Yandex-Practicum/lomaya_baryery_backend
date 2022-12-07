import enum
from datetime import date, datetime, timedelta
from typing import Optional

from pydantic import Field, root_validator, validator

from src.api.request_models.request_base import RequestBase


class ShiftSortRequest(str, enum.Enum):
    """Поля модели Shift для сортировки."""

    STATUS = "status"
    STARTED_AT = "started_at"
    FINISHED_AT = "finished_at"


class ShiftCreateRequest(RequestBase):
    started_at: datetime
    finished_at: datetime
    title: str = Field(..., min_length=3, max_length=100)

    @validator("started_at")
    def validate_started_later_than_now(cls, value: datetime) -> datetime:
        if value.date() < date.today():
            raise ValueError("Дата начала смены не может быть меньше текущей")
        return value

    @validator("finished_at")
    def validate_finished_at_later_than_4_month(cls, value: datetime) -> datetime:
        if value.date() > (date.today() + timedelta(days=120)):
            raise ValueError("Дата окончания не может быть больше 4-х месяцев")
        return value

    @root_validator(skip_on_failure=True)
    def validate_finished_at_earlier_then_started(cls, values: dict) -> dict:
        if values["started_at"] > values["finished_at"]:
            raise ValueError("Дата начала смены не может быть больше даты окончания")
        return values


class ShiftUpdateRequest(ShiftCreateRequest):
    started_at: Optional[datetime] = Field(None)
    finished_at: Optional[datetime] = Field(None)
    title: Optional[str] = Field(None, max_length=100)
    final_message: Optional[str] = Field(None, max_length=400)
