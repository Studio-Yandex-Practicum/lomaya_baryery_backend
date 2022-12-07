from datetime import date
from uuid import UUID

from pydantic import BaseModel

from src.api.response_models.user import UserResponse
from src.core.db.models import Member, UserTask


class MemeberTaskShortResponse(BaseModel):
    """Cхема для отображения краткой информации об отчете (UserTask) участника смены (Shift)."""

    task_id: UUID
    status: UserTask.Status
    task_date: date

    class Config:
        orm_mode = True


class MemberResponse(BaseModel):
    """Схема для отображения информации об участнике смены (Shift)."""

    id: UUID
    status: Member.Status
    user: UserResponse
    user_tasks: list[MemeberTaskShortResponse]

    class Config:
        orm_mode = True
