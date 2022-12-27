from datetime import date, datetime
from typing import Optional
from uuid import UUID

from fastapi import Depends

from src.api.request_models.user import (
    RequestCreateRequest,
    UserCreateRequest,
    UserDescAscSortRequest,
    UserFieldSortRequest,
)
from src.api.response_models.user import UserWithStatusResponse
from src.core.db.models import Request, User
from src.core.db.repository.request_repository import RequestRepository
from src.core.db.repository.user_repository import UserRepository
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
        self, user_repository: UserRepository = Depends(), request_repository: RequestRepository = Depends()
    ) -> None:
        self.__user_repository = user_repository
        self.__request_repository = request_repository

    async def user_registration(self, new_user: UserCreateRequest):
        """Регистрация пользователя. Отправка запроса на участие в смене."""
        await validate_user_create(new_user, self.__user_repository)
        user = User(**new_user.dict())
        user.status = User.Status.PENDING
        await self.__user_repository.create(user)
        request = await self.__request_repository.get_or_none(user.id)
        if not request:
            new_request = RequestCreateRequest(user_id=user.id, status=Request.Status.PENDING)
            request = Request(**new_request.dict())
            await self.__user_repository.create(request)

    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
        """Получить участника проекта по его telegram_id."""
        return await self.__user_repository.get_by_telegram_id(telegram_id)

    async def get_user_by_id_with_shifts_detail(self, user_id: UUID):
        """Получить участника проекта с информацией о сменах по его id."""
        user = await self.__user_repository.get(user_id)
        list_user_shifts = await self.__user_repository.get_user_shifts_detail(user.id)
        user.shifts = [shift for shift in list_user_shifts if shift.id is not None]
        return user

    async def list_all_users(
        self,
        status: Optional[User.Status] = None,
        field_sort: Optional[UserFieldSortRequest] = None,
        direction_sort: Optional[UserDescAscSortRequest] = None,
    ) -> list[UserWithStatusResponse]:
        return await self.__user_repository.get_users_with_status(status, field_sort, direction_sort)
