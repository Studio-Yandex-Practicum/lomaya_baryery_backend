from datetime import date
from uuid import UUID

from pydantic import BaseModel

from src.core.db.models import User


class UserResponse(BaseModel):
    """Схема для отображения информации о пользователе."""

    id: UUID
    name: str
    surname: str
    date_of_birth: date
    city: str
    phone_number: str

    class Config:
        orm_mode = True


class UserInfoResponse(BaseModel):
    """Схема для отображения краткой информации о пользователе."""

    name: str
    surname: str


class UserWithStatusResponse(UserResponse):
    status: User.Status
