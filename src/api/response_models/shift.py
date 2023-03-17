from datetime import date
from uuid import UUID

from pydantic import BaseModel

from src.api.response_models.member import MemberResponse
from src.core.db.models import Request, Shift


class ShiftResponse(BaseModel):
    id: UUID
    status: Shift.Status
    title: str
    final_message: str
    started_at: date
    finished_at: date
    sequence_number: int

    class Config:
        orm_mode = True


class ShiftMembersResponse(BaseModel):
    """Модель для вывода пользователей смены."""

    members: list[MemberResponse]


class ShiftDtoResponse(BaseModel):
    user_id: UUID
    name: str
    surname: str
    date_of_birth: date
    city: str
    phone_number: str
    request_id: UUID
    request_status: Request.Status

    class Config:
        orm_mode = True


class ShiftWithTotalUsersResponse(ShiftResponse):
    total_users: int
