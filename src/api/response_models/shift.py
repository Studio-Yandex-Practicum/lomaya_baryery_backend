from datetime import date
from uuid import UUID

from pydantic import BaseModel

from src.core.db.models import Shift


class ShiftDBResponse(BaseModel):
    id: UUID
    status: Shift.Status
    started_at: date
    finished_at: date

    class Config:
        orm_mode = True
