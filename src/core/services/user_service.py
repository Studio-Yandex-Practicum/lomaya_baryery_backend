import re
from datetime import date, datetime

from fastapi import Depends
from phonenumbers import PhoneNumberFormat, format_number, is_valid_number, parse
from phonenumbers.phonenumberutil import NumberParseException
from pydantic import validator

from src.api.request_models.user import RequestCreateRequest, UserCreateRequest
from src.core.db.models import Request, User
from src.core.db.repository.request_repository import RequestRepository
from src.core.db.repository.user_repository import UserRepository
from src.core.settings import settings

VALID_TEXT = "^[а-яА-ЯёЁ][а-яА-ЯёЁ -]*[а-яА-ЯёЁ]$"
INVALID_TEXT_ERROR = "В поле {} использованы недопустимые символы.".format


class ValidateUserCreate(UserCreateRequest):
    """Валидация персональных данных пользователя."""

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

    @validator("date_of_birth")
    def validate_date_of_birth(cls, value: date):
        current_year = datetime.now().date().year
        if current_year - value.year < settings.MIN_AGE:
            raise ValueError(f'Возраст не может быть менее {settings.MIN_AGE} лет.')
        return value

    @validator("city")
    def validate_city(cls, value: str):
        correct_value = re.compile(VALID_TEXT).search(value)
        if not correct_value:
            raise ValueError(INVALID_TEXT_ERROR('Город'))
        return value.title()

    @validator("phone_number", pre=True)
    def validate_phone_number(cls, value: str):
        try:
            parsed_number = parse(value.replace('+', ''), "RU")
        except NumberParseException:
            raise ValueError('Некорректный номер телефона.')
        if not is_valid_number(parsed_number):
            raise ValueError('Некорректный номер телефона.')
        return format_number(parsed_number, PhoneNumberFormat.E164)[1:]


class UserService:
    def __init__(
        self, user_repository: UserRepository = Depends(), request_repository: RequestRepository = Depends()
    ) -> None:
        self.user_repository = user_repository
        self.request_repository = request_repository

    async def user_registration(self, user_data: dict):
        """Регистрация пользователя. Отправка запроса на участие в смене."""
        user_scheme = UserCreateRequest(**user_data)
        valid_user_scheme = ValidateUserCreate(**user_scheme.dict())
        user = await self.user_repository.get_by_telegram_id(valid_user_scheme.telegram_id)
        if not user:
            user = await self.user_repository.get_by_phone_number(valid_user_scheme.phone_number)
        if not user:
            user = User(**valid_user_scheme.dict())
            await self.user_repository.create(user)
        request = await self.request_repository.get_or_none(user.id)
        if not request:
            request_scheme = RequestCreateRequest(user_id=user.id, status=Request.Status.PENDING)
            request = Request(**request_scheme.dict())
            await self.user_repository.create(request)
