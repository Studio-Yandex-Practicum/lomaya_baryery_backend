from datetime import date, datetime, timedelta

from pydantic import validator

from .request_base import RequestBase


class ShiftCreateRequest(RequestBase):
    started_at: datetime
    finished_at: datetime

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
