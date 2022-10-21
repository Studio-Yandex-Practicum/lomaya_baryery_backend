import re
from datetime import date, datetime

from fastapi import Depends
from phonenumbers import PhoneNumberFormat, format_number, is_valid_number, parse
from phonenumbers.phonenumberutil import NumberParseException

from src.api.request_models.user import RequestCreateRequest, UserCreateRequest
from src.core.db.models import Request, User
from src.core.db.repository.request_repository import RequestRepository
from src.core.db.repository.user_repository import UserRepository
from src.core.settings import settings

VALID_TEXT = "^[а-яА-ЯёЁ][а-яА-ЯёЁ -]*[а-яА-ЯёЁ]$"
INVALID_TEXT_ERROR = "В поле {} могут быть использованы только русские буквы и \"-\".".format


def validate_text(value: str, field_name: str) -> str:
    """Валидация имени пользователя."""
    correct_value = re.compile(VALID_TEXT).search(value)
    if not correct_value:
        raise ValueError(INVALID_TEXT_ERROR(field_name))
    return value.title()


def validate_date_of_birth(value: date) -> date:
    """Валидация даты рождения пользователя."""
    current_year = datetime.now().date().year
    if current_year - value.year < settings.MIN_AGE:
        raise ValueError(f'Возраст не может быть менее {settings.MIN_AGE} лет.')
    return value


def validate_phone_number(value: str) -> str:
    """Валидация и форматирование телефонного номера пользователя."""
    try:
        parsed_number = parse(value.replace('+', ''), "RU")
    except NumberParseException:
        raise ValueError('Некорректный номер телефона.')
    if not is_valid_number(parsed_number):
        raise ValueError('Некорректный номер телефона.')
    return format_number(parsed_number, PhoneNumberFormat.E164)[1:]


async def validate_user_not_exists(
    user_repository: UserRepository, telegram_id: int = None, phone_number: str = None
) -> None:
    """Проверка, что в БД нет пользователя с указанным telegram_id или phone_number."""
    user_exists = await user_repository.check_user_existence(telegram_id, phone_number)
    if user_exists:
        raise ValueError('Пользователь уже зарегистрирован.')


async def validate_user_create(user: UserCreateRequest, user_repository: UserRepository) -> UserCreateRequest:
    """Валидация персональных данных пользователя."""
    user.name = validate_text(user.name, 'Имя')
    user.surname = validate_text(user.surname, 'Фамилия')
    user.date_of_birth = validate_date_of_birth(user.date_of_birth)
    user.city = validate_text(user.city, 'Город')
    user.phone_number = validate_phone_number(user.phone_number)
    await validate_user_not_exists(user_repository, user.telegram_id, user.phone_number)
    return user


class UserService:
    def __init__(
        self, user_repository: UserRepository = Depends(), request_repository: RequestRepository = Depends()
    ) -> None:
        self.user_repository = user_repository
        self.request_repository = request_repository

    async def user_registration(self, user_data: dict):
        """Регистрация пользователя. Отправка запроса на участие в смене."""
        user_scheme = UserCreateRequest(**user_data)
        valid_user_scheme = await validate_user_create(user_scheme, self.user_repository)
        user = User(**valid_user_scheme.dict())
        await self.user_repository.create(user)
        request = await self.request_repository.get_or_none(user.id)
        if not request:
            request_scheme = RequestCreateRequest(user_id=user.id, status=Request.Status.PENDING)
            request = Request(**request_scheme.dict())
            await self.user_repository.create(request)
