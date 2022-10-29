from typing import Optional

from pydantic import BaseModel


class HealthcheckResponse(BaseModel):
    """Модель для вывода статусов ручки /healthcheck."""

    bot_status: bool
    api_status: bool
    db_status: bool
    errors: Optional[list]
