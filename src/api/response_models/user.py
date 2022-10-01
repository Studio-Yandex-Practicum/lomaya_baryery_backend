from datetime import date
from uuid import UUID

from pydantic import BaseModel

from .shift import ShiftResponse


class UserResponseDB(BaseModel):
    """Модель пользователя для ответа."""

    user_id: UUID
    name: str
    surname: str
    date_of_birth: date
    city: str
    phone: str

    class Config:
        orm_mode = True


class UserListResponseModel(BaseModel):
    """Модель для вывода списка пользователей смены."""

    shift: ShiftResponse
    users: list[UserResponseDB]
