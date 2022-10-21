from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Модель для вывода статусов ручки /healthcheck."""
    bot_status: str
    api_status: str
    db_status: str
