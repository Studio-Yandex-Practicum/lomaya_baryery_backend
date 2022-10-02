from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from src.core.db.models import Request


class GetListAllShiftRequests(BaseModel):
    shift_id: UUID
    status: Optional[Request.Status]
