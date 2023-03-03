from pydantic import EmailStr, Field, SecretStr, validator

from src.api.request_models.request_base import RequestBase
from src.api.request_models.validators import name_surname_validator
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

    _validate_name = name_surname_validator("name")
    _validate_surname = name_surname_validator("surname")

    @validator("password")
    def validate_password(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value()) < settings.MIN_PASSWORD_LENGTH:
            raise ValueError(
                "Пароль слишком короткий. Минимальная длина пароля: {}.".format(settings.MIN_PASSWORD_LENGTH)
            )
        return value


class AdministratorListRequest(RequestBase):
    """Схема для запроса списка администраторов."""

    status: Administrator.Status | None
    role: Administrator.Role | None


class RefreshToken(RequestBase):
    """Схема для передачи refresh токена."""

    refresh_token: str
