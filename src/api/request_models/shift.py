from datetime import datetime

from pydantic import BaseModel, Field, root_validator

from src.core.db.models import Shift


class ShiftCreate(BaseModel):
    status: Shift.Status = Field("preparing")
    started_at: datetime
    finished_at: datetime

    @root_validator
    def check_started_later_than_finished(
        cls, values: list[Shift.Status, datetime, datetime]
    ) -> list[Shift.Status, datetime, datetime]:
        if values["started_at"] > values["finished_at"]:
            raise ValueError("Время начала смены " "не может быть больше конца")
        return values
