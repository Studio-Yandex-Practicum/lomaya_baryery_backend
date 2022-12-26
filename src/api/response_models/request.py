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
    request_status: enum.Enum
    user_status: enum.Enum

    @classmethod
    def parse_from(cls, obj: Request) -> RequestResponse:
        """Парсит модель sqlalchemy Request, полученной с помощью метода get класса RequestRepository."""
        return cls(
            request_id=obj.id,
            user_id=obj.user.id,
            name=obj.user.name,
            surname=obj.user.surname,
            date_of_birth=obj.user.date_of_birth,
            city=obj.user.city,
            phone_number=obj.user.phone_number,
            request_status=obj.status,
            user_status=obj.user.status,
        )
