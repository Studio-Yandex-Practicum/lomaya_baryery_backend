from datetime import date
from uuid import UUID

from pydantic import BaseModel


class RequestResponse(BaseModel):
    request_id: UUID
    user_id: UUID
    name: str
    surname: str
    date_of_birth: date
    city: str
    phone_number: str
    status: str
