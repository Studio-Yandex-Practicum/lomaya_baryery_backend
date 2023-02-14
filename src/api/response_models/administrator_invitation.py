from pydantic import BaseModel

from src.core.db.models import Administrator


class AdministratorInvitationResponse(BaseModel):
    """Схема для отображения информации о приглашении администратора."""

    name: str
    surname: str
    email: str
    role: str = Administrator.Role.PSYCHOLOGIST

    class Config:
        orm_mode = True
