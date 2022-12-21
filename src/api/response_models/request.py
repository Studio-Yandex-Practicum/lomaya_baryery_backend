from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel

from src.core.db.models import Request


class RequestResponseBase(BaseModel):
    request_id: UUID
    user_id: UUID
    name: str
    surname: str
    date_of_birth: date
    city: str
    phone_number: str

    @classmethod
    def parse_from(cls, request_obj: Request) -> RequestResponseBase:
        """Парсит модель sqlalchemy Request, полученной с помощью метода get класса RequestRepository."""
        return cls(
            request_id=request_obj.id,
            user_id=request_obj.user.id,
            name=request_obj.user.name,
            surname=request_obj.user.surname,
            date_of_birth=request_obj.user.date_of_birth,
            city=request_obj.user.city,
            phone_number=request_obj.user.phone_number,
            status=request_obj.status,
        )


class RequestResponse(RequestResponseBase):
    status: str


class RequestWithUserStatusResponse(RequestResponseBase):
    user_status: str
    request_status: str
