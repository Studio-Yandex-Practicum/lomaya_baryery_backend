import re
from datetime import datetime

from fastapi import Depends
from phonenumbers import PhoneNumberFormat, format_number, is_valid_number, parse

from src.api.request_models.user import RequestCreateRequest, UserCreateRequest
from src.core.db.models import Request, User
from src.core.db.repository.request_repository import RequestRepository
from src.core.db.repository.user_repository import UserRepository

VALID_TEXT = "^[a-zA-Zа-яА-ЯёЁ ]?[-a-zA-Zа-яА-ЯёЁ ]+[a-zA-Zа-яА-ЯёЁ ]$"
VALID_DATE_FORMAT = "%Y-%m-%d"


def validate_name_surname_city_callback(value: str) -> str:
    """Валидация имени, фамилии, названия города."""
    correct_value = re.compile(VALID_TEXT).search(value)
    if correct_value:
        return correct_value.group().title()


def validate_date_of_birth_callback(date: str) -> str:
    """Валидация даты рождения."""
    try:
        correct_date = datetime.strptime(date, VALID_DATE_FORMAT)
        if correct_date < datetime.now():
            return date
    except Exception:
        return


def validate_phone_number_callback(number: str) -> str:
    """Валидация номера телефона.

    Ввод в любых форматах с кодами региона (7, 8, +7, +8) или без кода
    Вывод в формате: 7[0-9]{10}
    """
    try:
        parsed_number = parse(number.replace('+', ''), "RU")
        if is_valid_number(parsed_number):
            return format_number(parsed_number, PhoneNumberFormat.E164)[1:]
    except Exception:
        return


VALID_PERSONAL_DATA_DICT = {
    'name': ('Имя', validate_name_surname_city_callback),
    'surname': ('Фамилия', validate_name_surname_city_callback),
    'date_of_birth': ('Дата рождения', validate_date_of_birth_callback),
    'city': ('Город', validate_name_surname_city_callback),
    'phone_number': ('Телефон', validate_phone_number_callback),
}


def validate_user_data(user_data: dict[str, str]) -> dict[str, str]:
    """Валидация персональных данных пользователя и возврат с форматированием."""
    correct_data = {}
    for key, value in user_data.items():
        if key not in VALID_PERSONAL_DATA_DICT:
            raise ValueError(f'Исключите лишнее поле - {key} ')
        field = VALID_PERSONAL_DATA_DICT[key]
        if not field[1](value):
            raise ValueError(f'Некорректно заполнено поле - {field[0]}')
        correct_data[key] = field[1](value)
    return correct_data


class UserService:
    def __init__(
        self, user_repository: UserRepository = Depends(), request_repository: RequestRepository = Depends()
    ) -> None:
        self.user_repository = user_repository
        self.request_repository = request_repository

    async def user_registration(self, user_data: dict):
        """Регистрация пользователя. Отправка запроса на участие в смене."""
        telegram_id = user_data.get("telegram_id")
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        if not user:
            user_scheme = UserCreateRequest(**user_data)
            user = User(**user_scheme.dict())
            await self.user_repository.create(user)
        request = await self.request_repository.get_or_none(user.id)
        if not request:
            request_scheme = RequestCreateRequest(user_id=user.id, status=Request.Status.PENDING)
            request = Request(**request_scheme.dict())
            await self.user_repository.create(request)
