from datetime import datetime

from pydantic import BaseModel


class AdministratorInvitationResponse(BaseModel):
    """Схема для отображения информации о приглашении администратора."""

    name: str
    surname: str
    email: str
    expired_datetime: datetime

    class Config:
        orm_mode = True
