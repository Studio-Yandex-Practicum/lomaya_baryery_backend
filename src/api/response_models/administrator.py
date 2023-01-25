from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.core.db.models import Administrator


class AdministratorResponse(BaseModel):
    """Схема для отображения информации об администраторе."""

    id: UUID
    name: str
    surname: str
    email: str
    role: Administrator.Role
    status: Administrator.Status

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    """Схема для отображения access и refresh токенов."""

    access_token: str
    refresh_token: str


class AdministratorListResponse(AdministratorResponse):
    """Схема для отображения списка администраторов."""

    last_login_at: datetime
