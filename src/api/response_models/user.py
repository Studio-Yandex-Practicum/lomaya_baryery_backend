from pydantic import BaseModel


class UserInfoResponse(BaseModel):
    """Схема для отображения информации о пользователе."""

    name: str
    surname: str
