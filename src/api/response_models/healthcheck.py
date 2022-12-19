from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ComponentItemHealthcheck(BaseModel):
    """Model for the statuses of each part of the app"""

    name: str
    status: bool = True
    errors: Optional[list[str]] = []


class HealthcheckResponse(BaseModel):
    """Model for displaying statuses from /healthcheck."""

    timestamp: datetime
    components: list[ComponentItemHealthcheck]
