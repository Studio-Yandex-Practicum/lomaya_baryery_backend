from datetime import date

from phonenumbers import phonenumber
from pydantic import BaseModel

from .shift import ShiftResponse


class UserResponseDB(BaseModel):
    """Модель пользователя для ответа."""

    user_id: int
    name: str
    surname: str
    date_of_birth: date
    city: str
    phone: phonenumber

    class Config:
        orm_mode = True


class UserListResponseModel(BaseModel):
    """Модель для вывода списка пользователей смены."""

    shift: ShiftResponse
    users: list[UserResponseDB]
