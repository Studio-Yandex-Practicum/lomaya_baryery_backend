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
    title: str = Field(..., max_length=50)

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
    def validate_started_at_and_finished_at_fields_together(cls, values):
        if values['started_at'].date() >= values['finished_at'].date():
            raise ValueError("Дата начала не может быть больше или равняться дате окончания")
        return values


class ShiftUpdateRequest(ShiftCreateRequest):
    started_at: Optional[datetime] = Field(None)
    finished_at: Optional[datetime] = Field(None)
    title: Optional[str] = Field(None, max_length=100)
    final_message: Optional[str] = Field(None, min_length=10, max_length=400)

    @root_validator(skip_on_failure=True)
    def validate_started_at_and_finished_at_fields_together(cls, values):
        if all((values['started_at'], values['finished_at'])):
            return super().validate_started_at_and_finished_at_fields_together(values)
        return values
