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
    password: SecretStr

    async def parse_to_db_obj(self) -> Administrator:
        administrator = Administrator()
        administrator.name = self.name
        administrator.surname = self.surname
        return administrator


class AdministratorListRequest(RequestBase):
    """Схема для запроса списка администраторов."""

    status: Administrator.Status | None
    role: Administrator.Role | None
