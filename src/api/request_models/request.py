import enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.core.db.models import Request


class Status(str, enum.Enum):
    """Статус рассмотренной заявки."""

    APPROVED = "approved"
    DECLINED = "declined"


class RequestStatusUpdateRequest(BaseModel):
    status: Status = Field(Status.APPROVED.value)


class GetListAllShiftRequests(BaseModel):
    shift_id: UUID
    status: Optional[Request.Status]
