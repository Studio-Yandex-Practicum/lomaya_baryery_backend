from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from src.core.db.models import Request

INVALID_TYPE_ERROR = 'В поле {} передан некорректный тип данных.'.format


class UserCreateRequest(BaseModel):
    telegram_id: int
    name: str = Field(min_length=2, max_length=100)
    surname: str = Field(min_length=2, max_length=100)
    date_of_birth: date
    city: str = Field(min_length=2, max_length=50)
    phone_number: str

    @validator("telegram_id", pre=True)
    def validate_telegram_id(cls, value: int):
        if not isinstance(value, int):
            raise ValueError(INVALID_TYPE_ERROR('Telegram ID'))
        return value

    @validator("name", pre=True)
    def validate_name(cls, value: str):
        if not isinstance(value, str):
            raise ValueError(INVALID_TYPE_ERROR('Имя'))
        return value

    @validator("surname", pre=True)
    def validate_surname(cls, value: str):
        if not isinstance(value, str):
            raise ValueError(INVALID_TYPE_ERROR('Фамилия'))
        return value

    @validator("date_of_birth", pre=True)
    def validate_date_of_birth(cls, value: date):
        if not isinstance(value, date):
            raise ValueError(INVALID_TYPE_ERROR('Дата рождения'))
        return value

    @validator("city", pre=True)
    def validate_city(cls, value: str):
        if not isinstance(value, str):
            raise ValueError(INVALID_TYPE_ERROR('Город'))
        return value

    @validator("phone_number", pre=True)
    def validate_phone_number(cls, value: str):
        if not isinstance(value, str):
            raise ValueError(INVALID_TYPE_ERROR('Телефон'))
        return value


class RequestCreateRequest(BaseModel):
    user_id: UUID
    shift_id: Optional[UUID] = None
    status: Request.Status
