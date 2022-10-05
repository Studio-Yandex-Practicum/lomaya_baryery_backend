import re
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ValidationError, validator

from src.core.db.models import Request

VALID_TEXT = "^[a-zA-Zа-яА-ЯёЁ ]+$"
VALID_PHONE_NUMBER = "^[0-9]{11}$"
INVALID_TEXT_ERROR = "Адрес содержит недопустимые символы"


class UserCreateRequest(BaseModel):
    telegram_id: int
    name: str = Field(min_length=2, max_length=100)
    surname: str = Field(min_length=2, max_length=100)
    date_of_birth: date
    city: str = Field(min_length=2, max_length=50)
    phone_number: Optional[str]
    deleted: bool = False

    @validator("date_of_birth", pre=True)
    def validate_date(cls, value: str):
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValidationError as error:
            return error

    @validator("name", pre=True)
    def validate_name(cls, value: str):
        if re.compile(VALID_TEXT).search(value) is None:
            raise ValueError(INVALID_TEXT_ERROR)
        return value.title()

    @validator("surname", pre=True)
    def validate_surname(cls, value: str):
        if re.compile(VALID_TEXT).search(value) is None:
            raise ValueError(INVALID_TEXT_ERROR)
        return value.title()

    @validator("city", pre=True)
    def validate_city(cls, value: str):
        if re.compile(VALID_TEXT).search(value) is None:
            raise ValueError(INVALID_TEXT_ERROR)
        return value.title()

    @validator("phone_number", pre=True)
    def validate_phone(cls, value):
        if re.compile(VALID_PHONE_NUMBER).search(str(value)) is None:
            raise ValueError("Поле телефона должно состоять из 11 цифр")
        return value


class RequestCreateRequest(BaseModel):
    user_id: UUID
    shift_id: Optional[UUID] = None
    status: Request.Status
