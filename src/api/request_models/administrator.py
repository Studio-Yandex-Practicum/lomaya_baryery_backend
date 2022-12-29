from pydantic import EmailStr, Field, SecretStr

from src.api.request_models.request_base import RequestBase
from src.core.db.models import Administrator


class AdministratorAuthenticateRequest(RequestBase):
    """Схема для аутентификации администратора."""

    email: EmailStr
    password: SecretStr


class AdministratorCreateRequest(AdministratorAuthenticateRequest):
    """Схема для создания администратора."""

    name: str = Field(min_length=2, max_length=100)
    surname: str = Field(min_length=2, max_length=100)

    def create_administrator_instance(self):
        administrator = Administrator(**self.dict(exclude={"password"}))
        administrator.status = Administrator.Status.ACTIVE
        return administrator
