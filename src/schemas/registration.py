from enum import Enum
from pydantic import BaseModel, UUID4
from typing import Optional


class RequestStatus(str, Enum):
    approved = 'approved'
    declined = 'declined'
    pending = 'pending'


class RequestData(BaseModel):
    user_id: UUID4
    shift_id: Optional[UUID4] = None
    status: RequestStatus = RequestStatus.pending
