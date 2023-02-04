from uuid import UUID

from pydantic import EmailStr, Field, SecretStr

from src.api.request_models.request_base import RequestBase
from src.core.db.models import Administrator


class AdministratorAuthenticateRequest(RequestBase):
    """Схема для аутентификации администратора."""

    email: EmailStr
    password: SecretStr


class AdministratorRegistrationRequest(RequestBase):
    """Схема для регистрации администратора."""

    name: str = Field(min_length=2, max_length=100)
    surname: str = Field(min_length=2, max_length=100)
    role: Administrator.Role
    password: SecretStr
    token: UUID


class AdministratorListRequest(RequestBase):
    """Схема для запроса списка администраторов."""

    status: Administrator.Status | None
    role: Administrator.Role | None
