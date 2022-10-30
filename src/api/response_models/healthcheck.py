from pydantic import BaseModel


class HealthcheckResponse(BaseModel):
    """Модель для вывода статусов ручки /healthcheck."""

    bot_status: tuple[bool] | tuple[bool, str]
    api_status: tuple[bool] | tuple[bool, str]
    db_status: tuple[bool] | tuple[bool, str]
