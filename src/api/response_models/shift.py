from datetime import date
from uuid import UUID

from pydantic import BaseModel

from src.api.response_models.user import UserResponse
from src.core.db.models import Shift


class ShiftResponse(BaseModel):
    id: UUID
    status: Shift.Status
    started_at: date
    finished_at: date

    class Config:
        orm_mode = True


class ShiftUsersResponse(BaseModel):
    """Модель для вывода пользователей смены."""

    shift: ShiftResponse
    users: list[UserResponse]
