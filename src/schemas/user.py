import re
from typing import Optional
from pydantic import BaseModel, validator, Field, ValidationError
from datetime import date
from dateutil.parser import parse


class UserData(BaseModel):
    telegram_id: int
    name: str = Field(..., min_length=2, max_length=100)
    surname: str = Field(..., min_length=2, max_length=100)
    date_of_birth: date
    city: str = Field(..., min_length=2, max_length=50)
    phone_number: Optional[str]
    deleted: bool = False

    @validator('date_of_birth', pre=True)
    def date_parse(cls, value: str):
        try:
            return parse(value)
        except ValidationError as error:
            return error

    @validator('name', pre=True)
    def name_title(cls, value: str):
        regex = "^[a-zA-Zа-яА-ЯёЁ ]+$"
        if re.compile(regex).search(value) is None:
            raise ValueError('Адрес содержит недопустимые символы')
        return value.title()

    @validator('surname', pre=True)
    def surname_title(cls, value: str):
        regex = "^[a-zA-Zа-яА-ЯёЁ ]+$"
        if re.compile(regex).search(value) is None:
            raise ValueError('Адрес содержит недопустимые символы')
        return value.title()

    @validator('city', pre=True)
    def city_title(cls, value: str):
        regex = "^[a-zA-Zа-яА-ЯёЁ -]+$"
        if re.compile(regex).search(value) is None:
            raise ValueError('Адрес содержит недопустимые символы')
        return value.title()

    @validator('phone_number', pre=True)
    def phone_length(cls, value):
        regex = '^[0-9]{11}$'
        if re.compile(regex).search(str(value)) is None:
            raise ValueError('Поле телефона должно состоять из 11 цифр')
        return value

