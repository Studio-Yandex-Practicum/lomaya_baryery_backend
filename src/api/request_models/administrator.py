from pydantic import EmailStr, Field, SecretStr, StrictStr, validator

from src.api.request_models.request_base import RequestBase
from src.api.request_models.validators import name_surname_validator
from src.core.db.models import Administrator
from src.core.settings import settings


class AdministratorAuthenticateRequest(RequestBase):
    """Схема для аутентификации администратора."""

    email: EmailStr
    password: SecretStr


class AdministratorUpdateNameAndSurnameRequest(RequestBase):
    """Схема для обновления имени и фамилии администратора."""

    name: StrictStr = Field(min_length=2, max_length=100)
    surname: StrictStr = Field(min_length=2, max_length=100)

    _validate_name = name_surname_validator("name")
    _validate_surname = name_surname_validator("surname")


class AdministratorRegistrationRequest(AdministratorUpdateNameAndSurnameRequest):
    """Схема для регистрации администратора."""

    password: SecretStr

    @validator("password")
    def validate_password(cls, value: SecretStr) -> SecretStr:
        password = value.get_secret_value()
        if len(password) < settings.MIN_PASSWORD_LENGTH:
            raise ValueError(
                "Пароль слишком короткий. Минимальная длина пароля: {}.".format(settings.MIN_PASSWORD_LENGTH)
            )
        if not all(
            (
                any(s.isupper() for s in password),
                any(s.islower() for s in password),
                any(s.isdigit() for s in password),
            )
        ):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву, одну строчную и одну цифру.")
        return value


class AdministratorPasswordResetRequest(RequestBase):
    """Схема для запроса восстановления пароля администратора или эксперта."""

    email: EmailStr


class AdministratorRoleRequest(RequestBase):
    """Схема для запроса на смену роли администратора."""

    role: Administrator.Role


class AdministratorStatusRequest(RequestBase):
    """Схема для запроса на смену статуса администратора."""

    status: Administrator.Status
