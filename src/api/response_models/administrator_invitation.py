from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AdministratorInvitationResponse(BaseModel):
    """Схема для отображения информации о приглашенном администраторе."""

    id: UUID
    name: str
    surname: str
    email: str
    expired_datetime: datetime

    class Config:
        orm_mode = True
