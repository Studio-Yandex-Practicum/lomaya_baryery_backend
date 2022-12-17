import enum
from typing import Optional

from pydantic import BaseModel, Field

from src.api.request_models.request_base import RequestBase


class Status(str, enum.Enum):
    """Статус рассмотренной заявки."""

    APPROVED = "approved"
    DECLINED = "declined"
    EXCLUDED = "excluded"


class RequestStatusUpdateRequest(BaseModel):
    status: Status = Field(Status.APPROVED.value)


class RequestDeclineRequest(RequestBase):
    message: Optional[str] = None
