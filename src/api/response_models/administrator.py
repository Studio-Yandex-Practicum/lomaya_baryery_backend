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
    last_login_at: datetime | None

    class Config:
        orm_mode = True


class TwoTokensAdministratorResponse(BaseModel):
    """Схема для передачи access-, refresh-токенов и информации об администраторе."""

    access_token: str
    refresh_token: str
    id: UUID
    name: str
    surname: str
    email: str
    role: Administrator.Role
    status: Administrator.Status
    last_login_at: datetime | None


class TokenAdministratorResponse(BaseModel):
    """Схема для отображения access-токена и информации об администраторе."""

    access_token: str
    id: UUID
    name: str
    surname: str
    email: str
    role: Administrator.Role
    status: Administrator.Status
    last_login_at: datetime | None

    class Config:
        orm_mode = True
