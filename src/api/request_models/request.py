import enum

from pydantic import BaseModel, Field


class Status(str, enum.Enum):
    """Статус рассмотренной заявки."""

    APPROVED = "approved"
    DECLINED = "declined"


class RequestStatusUpdateRequest(BaseModel):
    status: Status = Field(Status.APPROVED.value)
