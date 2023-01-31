from datetime import date
from uuid import UUID

from pydantic import BaseModel


class AdministratorInvitationResponse(BaseModel):
    """Схема для отображения информации о приглашенном администраторе."""

    name: str
    surname: str
    email: str
    expired_date: date
    token: UUID

    class Config:
        orm_mode = True
