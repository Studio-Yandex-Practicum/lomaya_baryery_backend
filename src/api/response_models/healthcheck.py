from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PartHealthcheck(BaseModel):
    """Модель для вывода статусов каждой части приложения ручки /healthcheck."""

    status: bool
    errors: Optional[list[str]]


class ComponentsHealthcheck(BaseModel):
    """Модель статусов всех частей ручки /healthcheck."""

    bot: PartHealthcheck
    api: PartHealthcheck
    db: PartHealthcheck


class HealthcheckResponse(BaseModel):
    """Общая модель для вывода статусов ручки /healthcheck."""

    timestamp: datetime
    components: ComponentsHealthcheck
