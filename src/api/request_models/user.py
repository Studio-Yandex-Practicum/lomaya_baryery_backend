import re
from typing import Optional
from uuid import UUID

from phonenumbers import PhoneNumberFormat, format_number, is_valid_number, parse
from phonenumbers.phonenumberutil import NumberParseException
from pydantic import BaseModel, Field, PastDate, StrictInt, StrictStr, validator

from src.core.db.models import Request

VALID_TEXT = "^[а-яА-ЯёЁ][а-яА-ЯёЁ -]*[а-яА-ЯёЁ]$"
INVALID_TEXT_ERROR = "В поле {} могут быть использованы только русские буквы и \"-\".".format


class UserCreateRequest(BaseModel):
    telegram_id: StrictInt
    name: StrictStr = Field(min_length=2, max_length=100)
    surname: StrictStr = Field(min_length=2, max_length=100)
    date_of_birth: PastDate
    city: StrictStr = Field(min_length=2, max_length=50)
    phone_number: StrictStr

    @validator("name")
    def validate_name(cls, value: str):
        correct_value = re.compile(VALID_TEXT).search(value)
        if not correct_value:
            raise ValueError(INVALID_TEXT_ERROR('Имя'))
        return value.title()

    @validator("surname")
    def validate_surname(cls, value: str):
        correct_value = re.compile(VALID_TEXT).search(value)
        if not correct_value:
            raise ValueError(INVALID_TEXT_ERROR('Фамилия'))
        return value.title()

    @validator("city")
    def validate_city(cls, value: str):
        correct_value = re.compile(VALID_TEXT).search(value)
        if not correct_value:
            raise ValueError(INVALID_TEXT_ERROR('Город'))
        return value.title()

    @validator("phone_number", pre=True)
    def validate_phone_number(cls, value: str):
        invalid_phone_number = 'Некорректный номер телефона'
        try:
            parsed_number = parse(value.replace('+', ''), "RU")
        except NumberParseException:
            raise ValueError(invalid_phone_number)
        if not is_valid_number(parsed_number):
            raise ValueError(invalid_phone_number)
        return format_number(parsed_number, PhoneNumberFormat.E164)[1:]


class RequestCreateRequest(BaseModel):
    user_id: UUID
    shift_id: Optional[UUID] = None
    status: Request.Status
