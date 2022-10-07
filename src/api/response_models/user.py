from datetime import date
from uuid import UUID

from pydantic import BaseModel


class UserResponse(BaseModel):
    """Модель пользователя для ответа."""

    id: UUID
    name: str
    surname: str
    date_of_birth: date
    city: str
    phone_number: str

    class Config:
        orm_mode = True


class UserInfoResponse(BaseModel):
    """Схема для отображения информации о пользователе."""

    name: str
    surname: str
