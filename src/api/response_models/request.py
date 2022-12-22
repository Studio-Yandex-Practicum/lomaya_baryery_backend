from __future__ import annotations

import enum
from datetime import date
from uuid import UUID

from pydantic import BaseModel

from src.core.db.models import Request


class RequestResponse(BaseModel):
    request_id: UUID
    user_id: UUID
    name: str
    surname: str
    date_of_birth: date
    city: str
    phone_number: str
    status: enum.Enum

    @classmethod
    def parse_from(cls, request_obj: Request) -> RequestResponse:
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


class RequestWithUserStatusResponse(RequestResponse):
    user_status: enum.Enum
