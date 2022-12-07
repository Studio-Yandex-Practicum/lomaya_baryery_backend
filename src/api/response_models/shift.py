from datetime import date
from uuid import UUID

from pydantic import BaseModel

from src.api.response_models.user import UserResponse
from src.core.db.models import Request, Shift


class ShiftResponse(BaseModel):
    id: UUID
    status: Shift.Status
    title: str
    final_message: str
    started_at: date
    finished_at: date

    class Config:
        orm_mode = True


class ShiftUsersResponse(BaseModel):
    """Модель для вывода пользователей смены."""

    shift: ShiftResponse
    users: list[UserResponse]


class ShiftDtoRespone(BaseModel):
    user_id: UUID
    name: str
    surname: str
    date_of_birth: date
    city: str
    phone: str
    request_id: UUID
    status: Request.Status

    class Config:
        orm_mode = True


class ShiftWithTotalUsersResponse(ShiftResponse):
    sequence_number: int
    total_users: int
