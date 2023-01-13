from pydantic import EmailStr, SecretStr

from src.api.request_models.request_base import RequestBase


class AdministratorAuthenticateRequest(RequestBase):
    """Схема для аутентификации администратора."""

    email: EmailStr
    password: SecretStr
