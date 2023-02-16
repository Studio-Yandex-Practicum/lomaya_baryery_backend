import re

from pydantic import EmailStr, Field, SecretStr, validator

from src.api.request_models.request_base import RequestBase
from src.api.request_models.user import INVALID_TEXT_ERROR, VALID_TEXT
from src.core.db.models import Administrator
from src.core.settings import settings


class AdministratorAuthenticateRequest(RequestBase):
    """Схема для аутентификации администратора."""

    email: EmailStr
    password: SecretStr


class AdministratorRegistrationRequest(RequestBase):
    """Схема для регистрации администратора."""

    name: str = Field(min_length=2, max_length=100)
    surname: str = Field(min_length=2, max_length=100)
    password: SecretStr

    @validator("name")
    def validate_name(cls, value: str) -> str:
        if not re.compile(VALID_TEXT).match(value):
            raise ValueError(INVALID_TEXT_ERROR.format("Имя"))
        return value.title()

    @validator("surname")
    def validate_surname(cls, value: str) -> str:
        if not re.compile(VALID_TEXT).match(value):
            raise ValueError(INVALID_TEXT_ERROR.format("Фамилия"))
        return value.title()

    @validator("password")
    def validate_password(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value()) < settings.MIN_PASSWORD_LENGTH:
            raise ValueError(
                "Пароль слишком короткий. Минимальная длина пароля: {}.".format(settings.MIN_PASSWORD_LENGTH)
            )
        return value

    async def parse_to_db_obj(self) -> Administrator:
        administrator = Administrator()
        administrator.name = self.name
        administrator.surname = self.surname
        return administrator


class AdministratorListRequest(RequestBase):
    """Схема для запроса списка администраторов."""

    status: Administrator.Status | None
    role: Administrator.Role | None
