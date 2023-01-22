import enum
import re
from datetime import date, datetime
from typing import Optional, Union
from uuid import UUID

import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from pydantic import BaseModel, Field, PastDate, StrictInt, StrictStr, validator

from src.core.db.models import Request

VALID_TEXT = "^[а-яА-ЯёЁ][а-яА-ЯёЁ -]*[а-яА-ЯёЁ]$"
INVALID_TEXT_ERROR = "В поле {} могут быть использованы только русские буквы и \"-\"."
DATE_FORMAT = "%d.%m.%Y"


class UserCreateRequest(BaseModel):
    telegram_id: Optional[StrictInt]
    name: StrictStr = Field(min_length=2, max_length=100)
    surname: StrictStr = Field(min_length=2, max_length=100)
    date_of_birth: PastDate
    city: StrictStr = Field(min_length=2, max_length=50)
    phone_number: StrictStr

    @validator("name")
    def validate_name(cls, value: str):
        if not re.compile(VALID_TEXT).match(value):
            raise ValueError(INVALID_TEXT_ERROR.format('Имя'))
        return value.title()

    @validator("surname")
    def validate_surname(cls, value: str):
        if not re.compile(VALID_TEXT).match(value):
            raise ValueError(INVALID_TEXT_ERROR.format('Фамилия'))
        return value.title()

    @validator("city")
    def validate_city(cls, value: str):
        if not re.compile(VALID_TEXT).match(value):
            raise ValueError(INVALID_TEXT_ERROR.format('Город'))
        return value.title()

    @validator("phone_number", pre=True)
    def validate_phone_number(cls, value: str):
        invalid_phone_number = 'Некорректный номер телефона'
        try:
            parsed_number = phonenumbers.parse(value.replace('+', ''), "RU")
        except NumberParseException:
            raise ValueError(invalid_phone_number)
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValueError(invalid_phone_number)
        return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)[1:]

    @validator("date_of_birth", pre=True)
    def validate_date_of_birth(cls, value: str):
        return datetime.strptime(value, DATE_FORMAT).date()


class RequestCreateRequest(BaseModel):
    user_id: UUID
    shift_id: Optional[UUID] = None
    status: Request.Status


class UserFieldSortRequest(str, enum.Enum):
    """Поля модели User для сортировки по полю."""

    NAME = "name"
    SURNAME = "surname"
    DATE_OF_BIRTH = "date_of_birth"


class UserDescAscSortRequest(str, enum.Enum):
    """Поля модели User для сортировки по убыванию или возрастанию."""

    ASC = "asc"
    DESC = "desc"


class UserWebhookTelegram(BaseModel):
    """
    Валидируем и отдаем данные из базы в Query-форму.

    Если поля переданы не были, возвращаем пустой словарь.

    Optional и root_validator - необходимы если пользователя нет в базе.

    - **name**: провалидированное имя пользователя
    - **surname**: провалидированная фамилия пользовтаеля
    - **date_of_birth**: Хранится в бд с отличным форматом
    - **city**: Провалидированный город, хранящиеся в БД
    - ***phone_number**: Провалидированный телефон, хранящиеся в БД
    - **validate_date_of_birth**: Конвертация в нужный формат WebAppInfo
    """

    name: Optional[StrictStr]
    surname: Optional[StrictStr]
    date_of_birth: Optional[date]
    city: Optional[StrictStr]
    phone_number: Optional[int]

    @validator("date_of_birth")
    def fix_date_of_birth(cls, value: Union[date, None]) -> Union[str, None]:
        if value is not None:
            return value.strftime(DATE_FORMAT)
