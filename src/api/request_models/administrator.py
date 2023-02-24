from pydantic import EmailStr, SecretStr

from src.api.request_models.request_base import RequestBase
from src.core.db.models import Administrator


class AdministratorAuthenticateRequest(RequestBase):
    """Схема для аутентификации администратора."""

    email: EmailStr
    password: SecretStr


class AdministratorListRequest(RequestBase):
    """Схема для запроса списка администраторов."""

    status: Administrator.Status | None
    role: Administrator.Role | None


class RefreshToken(RequestBase):
    """Модель для отображения refresh токена."""

    refresh_token: str
