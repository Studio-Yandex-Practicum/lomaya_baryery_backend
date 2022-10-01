from typing import Optional

from pydantic import UUID4, BaseModel

from src.core.db.models import Request


class RequestCreate(BaseModel):
    user_id: UUID4
    shift_id: Optional[UUID4] = None
    status: Request.Status = Request.Status.PENDING
