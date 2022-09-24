from datetime import date
from pydantic import BaseModel

from src.core.db.models import Shift


class ShiftDB(BaseModel):
    id: int
    status: Shift.Status
    started_at: date
    finished_at: date

    class Config:
        orm_mode = True
