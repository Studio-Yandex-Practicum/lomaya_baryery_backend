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


class UsersShiftDetailResponse(BaseModel):
    """Схема для отображения информации о смене пользователя.

    Дополнительно отображается информации о количестве: заработанных за смену
    "ломбарьерчиков", одобренных, отмененных и пропущенных заданиях.
    """

    id: UUID
    title: str
    started_at: date
    finished_at: date
    numbers_lombaryers: int
    total_approved: int
    total_declined: int
    total_skipped: int

    class Config:
        orm_mode = True


class UserDetailResponse(UserResponse):
    """Схема для отображения информации о пользователе.

    Дополнительно отображается информация о сменах, в которых участвовал
    пользователь.
    """

    shifts: list[UsersShiftDetailResponse]
