from datetime import datetime

from pydantic import BaseModel, Field, root_validator

from src.core.db.models import Shift


class ShiftCreateRequest(BaseModel):
    status: Shift.Status = Field("preparing")
    started_at: datetime
    finished_at: datetime

    @root_validator
    def validate_started_later_than_finished(cls, values: dict) -> dict:
        if values["started_at"] > values["finished_at"]:
            raise ValueError("Время начала смены не может быть больше конца")
        return values
