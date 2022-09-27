from pydantic import BaseModel
from uuid import UUID


class RequestList(BaseModel):
    shift_id: UUID
    status: str
