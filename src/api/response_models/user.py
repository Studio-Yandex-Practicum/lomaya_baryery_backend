from datetime import date
from uuid import UUID

from pydantic import BaseModel

from src.core.db.models import Report


class ReportShortResponse(BaseModel):
    """Cхема, для передачи её в информацию о конкретной смене."""

    task_id: UUID
    status: Report.Status
    task_date: date

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    """Схема для отображения информации о пользователе."""

    id: UUID
    name: str
    surname: str
    date_of_birth: date
    city: str
    phone_number: str
    reports: list[ReportShortResponse]

    class Config:
        orm_mode = True


class UserInfoResponse(BaseModel):
    """Схема для отображения краткой информации о пользователе."""

    name: str
    surname: str
