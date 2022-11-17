from datetime import date
from uuid import UUID

from pydantic import BaseModel

from src.core.db.models import UserTask


class UserTaskShortResponse(BaseModel):
    """Cхема, для передачи её в информацию о конкретной смене."""

    task_id: UUID
    status: UserTask.Status
    task_date: date

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    """Модель пользователя для ответа."""

    id: UUID
    name: str
    surname: str
    date_of_birth: date
    city: str
    phone_number: str
    user_tasks: list[UserTaskShortResponse]

    class Config:
        orm_mode = True


class UserInfoResponse(BaseModel):
    """Схема для отображения информации о пользователе."""

    name: str
    surname: str
