from typing import Optional

from pydantic import BaseModel, Field

from src.api.request_models.request_base import RequestBase
from src.core.db.models import Request


class RequestStatusUpdateRequest(BaseModel):
    status: Request.Status = Field(Request.Status.APPROVED.value)


class RequestDeclineRequest(RequestBase):
    message: Optional[str] = None
