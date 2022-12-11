import enum
from datetime import date, datetime, timedelta

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
    title: str = Field(..., max_length=100)

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
    final_message: str = Field(..., min_length=10, max_length=400)
