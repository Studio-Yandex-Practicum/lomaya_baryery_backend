from pydantic import EmailStr, Field, SecretStr

from src.api.request_models.request_base import RequestBase


class AdministratorCreateRequest(RequestBase):
    """Схема для создания администратора."""

    name: str = Field(min_length=2, max_length=100)
    surname: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: SecretStr = Field(min_length=8, max_length=50)


class AdministratorAuthenticateRequest(RequestBase):
    """Схема для аутентификации администратора."""

    email: str
    password: str
