from pydantic import BaseModel


class AdministratorInvitationResponse(BaseModel):
    """Схема для отображения информации о приглашенном администраторе."""

    name: str
    surname: str
    email: str

    class Config:
        orm_mode = True
