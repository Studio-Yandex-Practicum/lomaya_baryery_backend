from pydantic import BaseModel


class HealthcheckResponse(BaseModel):
    """Модель для вывода статусов ручки /healthcheck."""

    bot_status: tuple
    api_status: tuple
    db_status: tuple
