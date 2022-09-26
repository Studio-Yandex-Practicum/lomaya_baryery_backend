from datetime import date
from uuid import UUID

from pydantic import BaseModel


class ShiftResponseModel(BaseModel):
    """Модель смены для ответа."""

    id: UUID
    status: str
    started_at: date
    finished_at: date

    class Config:
        orm_mode = True
