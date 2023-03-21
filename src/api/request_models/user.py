import enum
import re
from datetime import date, datetime
from typing import Optional
from uuid import UUID

import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from pydantic import BaseModel, Field, PastDate, StrictInt, StrictStr, validator

from src.api.request_models.validators import name_surname_validator
from src.core.db.models import Request, User

VALID_CITY_TEXT = r"^[А-ЯЁ][а-яё]*(([-][А-ЯЁ][а-яё]+)|[-](на)+)*([\s][А-ЯЁ][а-яё]+)*$"
INVALID_TEXT_ERROR = "В поле {} может быть использована только кириллица и \"-\"."
DATE_FORMAT = "%d.%m.%Y"


class UserCreateRequest(BaseModel):
    telegram_id: Optional[StrictInt]
    name: StrictStr = Field(min_length=2, max_length=100)
    surname: StrictStr = Field(min_length=2, max_length=100)
    date_of_birth: PastDate
    city: StrictStr = Field(min_length=2, max_length=50)
    phone_number: StrictStr

    _validate_name = name_surname_validator("name")
    _validate_surname = name_surname_validator("surname")

    @validator("city")
    def validate_city(cls, value: str):
        if not re.compile(VALID_CITY_TEXT).match(value):
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

    def create_db_model(self) -> User:
        user = User()
        return self.update_db_model(user)

    def update_db_model(self, user: User) -> User:
        user.telegram_id = self.telegram_id
        user.name = self.name
        user.surname = self.surname
        user.date_of_birth = self.date_of_birth
        user.city = self.city
        user.phone_number = self.phone_number
        return user

    def compare_with_db_model(self, user: User) -> bool:
        return all(
            (
                self.telegram_id == user.telegram_id,
                self.name == user.name,
                self.surname == user.surname,
                self.date_of_birth == user.date_of_birth,
                self.city == user.city,
                self.phone_number == user.phone_number,
            )
        )


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

    - **name**: провалидированное имя пользователя
    - **surname**: провалидированная фамилия пользовтаеля
    - **date_of_birth**: Хранится в бд с отличным форматом
    - **city**: Провалидированный город, хранящиеся в БД
    - ***phone_number**: Провалидированный телефон, хранящиеся в БД
    - **validate_date_of_birth**: Конвертация в нужный формат WebAppInfo
    """

    name: StrictStr
    surname: StrictStr
    date_of_birth: date
    city: StrictStr
    phone_number: int

    @validator("date_of_birth")
    def fix_date_of_birth(cls, value: date) -> str:
        return value.strftime(DATE_FORMAT)

    class Config:
        orm_mode = True
