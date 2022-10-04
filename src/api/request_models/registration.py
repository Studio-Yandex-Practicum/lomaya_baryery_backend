from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from src.core.db.models import Request


class RequestCreateRequest(BaseModel):
    user_id: UUID
    shift_id: Optional[UUID] = None
    status: Request.Status = Request.Status.PENDING
