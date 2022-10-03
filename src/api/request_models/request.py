import enum

from pydantic import BaseModel, Field


class Status(str, enum.Enum):
    """Статус рассмотренной заявки."""

    APPROVED = "approved"
    DECLINED = "declined"


class RequestStatusUpdate(BaseModel):
    status: Status = Field(Status.APPROVED.value)
