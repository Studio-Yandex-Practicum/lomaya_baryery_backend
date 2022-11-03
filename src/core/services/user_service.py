from datetime import date, datetime

from src.api.request_models.user import RequestCreateRequest, UserCreateRequest
from src.core.db.models import Request, User
from src.core.db.repository.request_repository import (
    RequestRepository,
    request_repository,
)
from src.core.db.repository.user_repository import UserRepository, user_repository
from src.core.settings import settings


def validate_date_of_birth(value: date) -> None:
    """Валидация даты рождения пользователя."""
    current_year = datetime.now().date().year
    if current_year - value.year < settings.MIN_AGE:
        raise ValueError(f'Возраст не может быть менее {settings.MIN_AGE} лет.')


async def validate_user_not_exists(
    user_repository: UserRepository, telegram_id: int = None, phone_number: str = None
) -> None:
    """Проверка, что в БД нет пользователя с указанным telegram_id или phone_number."""
    user_exists = await user_repository.check_user_existence(telegram_id, phone_number)
    if user_exists:
        raise ValueError('Пользователь уже зарегистрирован.')


async def validate_user_create(user: UserCreateRequest, user_repository: UserRepository) -> None:
    """Валидация персональных данных пользователя."""
    validate_date_of_birth(user.date_of_birth)
    await validate_user_not_exists(user_repository, user.telegram_id, user.phone_number)


class UserService:
    def __init__(
        self,
        user_repository: UserRepository = user_repository,
        request_repository: RequestRepository = request_repository,
    ) -> None:
        self.user_repository = user_repository
        self.request_repository = request_repository

    async def user_registration(self, user_data: dict):
        """Регистрация пользователя. Отправка запроса на участие в смене."""
        user_scheme = UserCreateRequest(**user_data)
        await validate_user_create(user_scheme, self.user_repository)
        user = User(**user_scheme.dict())
        await self.user_repository.create(user)
        request = await self.request_repository.get_or_none(user.id)
        if not request:
            request_scheme = RequestCreateRequest(user_id=user.id, status=Request.Status.PENDING)
            request = Request(**request_scheme.dict())
            await self.user_repository.create(request)
