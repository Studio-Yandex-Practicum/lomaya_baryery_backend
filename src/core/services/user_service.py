from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import Depends

from src.api.request_models.user import (
    UserCreateRequest,
    UserDescAscSortRequest,
    UserFieldSortRequest,
)
from src.api.response_models.user import UserDetailResponse, UserWithStatusResponse
from src.core.db.models import Request, User
from src.core.db.repository.request_repository import RequestRepository
from src.core.db.repository.user_repository import UserRepository
from src.core.exceptions import (
    AlreadyRegisteredException,
    NotValidValue,
    RequestForbiddenException,
)
from src.core.services.shift_service import ShiftService
from src.core.settings import settings


def validate_date_of_birth(value: date) -> None:
    """Валидация даты рождения пользователя."""
    current_date = date.today()
    if current_date.year - value.year < settings.MIN_AGE:
        raise NotValidValue(f'Возраст не может быть менее {settings.MIN_AGE} лет.')


async def validate_user_not_exists(
    user_repository: UserRepository, telegram_id: int = None, phone_number: str = None
) -> None:
    """Проверка, что в БД нет пользователя с указанным telegram_id или phone_number."""
    user_exists = await user_repository.check_user_existence(telegram_id, phone_number)
    if user_exists:
        raise NotValidValue('Пользователь с таким номером телефона уже существует.')


async def validate_user_create(user: UserCreateRequest, user_repository: UserRepository) -> None:
    """Валидация персональных данных пользователя."""
    validate_date_of_birth(user.date_of_birth)
    await validate_user_not_exists(user_repository, user.telegram_id, user.phone_number)


class UserService:
    def __init__(
        self,
        user_repository: UserRepository = Depends(),
        request_repository: RequestRepository = Depends(),
        shift_service: ShiftService = Depends(),
    ) -> None:
        self.__user_repository = user_repository
        self.__request_repository = request_repository
        self.__shift_service = shift_service

    async def register_user(self, new_user_data: UserCreateRequest) -> None:
        """Регистрация пользователя. Отправка запроса на участие в смене."""
        shift_id = await self.__shift_service.get_open_for_registration_shift_id()
        user = await self.__update_or_create_user(new_user_data)
        request = await self.__request_repository.get_by_user_and_shift(user.id, shift_id)
        if request:
            await self.__update_request_data(request)
        else:
            request = Request(user_id=user.id, shift_id=shift_id)
            await self.__request_repository.create(request)

    async def __update_request_data(self, request: Request) -> None:
        """Обработка повторного запроса пользователя на участие в смене."""
        if request.status is Request.Status.APPROVED:
            raise AlreadyRegisteredException
        if request.status is Request.Status.DECLINED:
            if request.is_repeated < settings.MAX_REQUESTS:
                request.is_repeated += 1
                request.status = Request.Status.PENDING
                await self.__request_repository.update(request.id, request)
            else:
                raise RequestForbiddenException

    async def __update_or_create_user(self, user_scheme: UserCreateRequest) -> User:
        """Получение пользователя: обновление или создание."""
        db_user = await self.__user_repository.get_by_telegram_id(user_scheme.telegram_id)
        if db_user:
            return await self.__update_user_if_data_changed(db_user, user_scheme)
        user = user_scheme.create_db_model()
        await validate_user_create(user_scheme, self.__user_repository)
        return await self.__user_repository.create(user)

    async def __update_user_if_data_changed(self, user: User, user_scheme: UserCreateRequest) -> User:
        """Обновление данных пользователя, если им внесены изменения."""
        if user_scheme.compare_with_db_model(user):
            return user
        validate_date_of_birth(user_scheme.date_of_birth)
        user.status = User.Status.PENDING
        user = user_scheme.update_db_model(user)
        return await self.__user_repository.update(user.id, user)

    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
        """Получить участника проекта по его telegram_id."""
        return await self.__user_repository.get_by_telegram_id(telegram_id)

    async def get_user_by_id_with_shifts_detail(self, user_id: UUID) -> UserDetailResponse:
        """Получить участника проекта с информацией о сменах по его id."""
        user = await self.__user_repository.get(user_id)
        list_user_shifts = await self.__user_repository.get_user_shifts_detail(user.id)
        user.shifts = list_user_shifts
        return user

    async def list_all_users(
        self,
        status: Optional[User.Status] = None,
        field_sort: Optional[UserFieldSortRequest] = None,
        direction_sort: Optional[UserDescAscSortRequest] = None,
    ) -> list[UserWithStatusResponse]:
        return await self.__user_repository.get_users_with_status(status, field_sort, direction_sort)

    async def set_telegram_blocked(self, user: User) -> None:
        user.telegram_blocked = True
        await self.__user_repository.update(user.id, user)

    async def unset_telegram_blocked(self, user: User) -> None:
        user.telegram_blocked = False
        await self.__user_repository.update(user.id, user)
