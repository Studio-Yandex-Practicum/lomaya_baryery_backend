from datetime import date
from uuid import UUID
from pydantic import BaseModel
from src.core.db.models import Request


class RequestDB(BaseModel):
    user_id: UUID
    name: str
    surname: str
    date_of_birth: date
    city: str
    phone: str
    request_id: UUID
    status: Request.Status

    class Config:
        orm_mode = True
