from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ComponentItemHealthcheck(BaseModel):
    """Model for the statuses of each part of the app"""

    status: bool
    errors: Optional[list[str]]


class ComponentsHealthcheck(BaseModel):
    """Model for all stratuses of the application"""

    bot: ComponentItemHealthcheck
    api: ComponentItemHealthcheck
    db: ComponentItemHealthcheck


class HealthcheckResponse(BaseModel):
    """Model for displaying statuses from /healthcheck."""

    timestamp: datetime
    components: ComponentsHealthcheck
