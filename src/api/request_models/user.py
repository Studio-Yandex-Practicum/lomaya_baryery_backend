from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, PastDate, StrictInt, StrictStr

from src.core.db.models import Request


class UserCreateRequest(BaseModel):
    telegram_id: StrictInt
    name: StrictStr = Field(min_length=2, max_length=100)
    surname: StrictStr = Field(min_length=2, max_length=100)
    date_of_birth: PastDate
    city: StrictStr = Field(min_length=2, max_length=50)
    phone_number: StrictStr


class RequestCreateRequest(BaseModel):
    user_id: UUID
    shift_id: Optional[UUID] = None
    status: Request.Status
