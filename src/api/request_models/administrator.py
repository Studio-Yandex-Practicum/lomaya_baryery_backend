from src.api.request_models.request_base import RequestBase


class AdministratorCreateRequest(RequestBase):
    """Схема для создания администратора."""

    name: str
    surname: str
    email: str
    password: str

    # TODO: валидация
