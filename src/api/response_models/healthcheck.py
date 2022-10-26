from typing import Optional

from pydantic import BaseModel


class HealthcheckResponse(BaseModel):
    """Модель для вывода статусов ручки /healthcheck."""

    bot_status: tuple[bool, Optional[str]]
    api_status: tuple[bool, Optional[str]]
    db_status: tuple[bool, Optional[str]]
