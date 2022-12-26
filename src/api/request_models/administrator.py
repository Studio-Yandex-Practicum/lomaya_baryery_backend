from pydantic import EmailStr, Field, SecretStr

from src.api.request_models.request_base import RequestBase


class AdministratorAuthenticateRequest(RequestBase):
    """Схема для аутентификации администратора."""

    email: EmailStr
    password: SecretStr


class AdministratorCreateRequest(AdministratorAuthenticateRequest):
    """Схема для создания администратора."""

    name: str = Field(min_length=2, max_length=100)
    surname: str = Field(min_length=2, max_length=100)
