from datetime import date
from typing import Optional

from fastapi import Depends

from src.api.request_models.user import (
    UserCreateRequest,
    UserDescAscSortRequest,
    UserFieldSortRequest,
)
from src.api.response_models.user import UserWithStatusResponse
from src.core.db.models import Request, User
from src.core.db.repository.request_repository import RequestRepository
from src.core.db.repository.user_repository import UserRepository
from src.core.exceptions import (
    AlreadyRegisteredException,
    MinAgeException,
    NoShiftForRegistrationException,
    RegistrationTakesTimeException,
    UserAlreadyExistException,
)
from src.core.services.shift_service import ShiftService
from src.core.settings import settings


def validate_date_of_birth(value: date) -> None:
    """Валидация даты рождения пользователя."""
    current_date = date.today()
    if current_date.year - value.year < settings.MIN_AGE:
        raise MinAgeException


async def validate_user_not_exists(
    user_repository: UserRepository, telegram_id: int = None, phone_number: str = None
) -> None:
    """Проверка, что в БД нет пользователя с указанным telegram_id или phone_number."""
    user_exists = await user_repository.check_user_existence(telegram_id, phone_number)
    if user_exists:
        raise UserAlreadyExistException


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

    async def user_registration(self, new_user_data: UserCreateRequest) -> None:
        """Регистрация пользователя. Отправка запроса на участие в смене."""
        shift_id = await self.__shift_service.get_shift_id_for_registration()
        if not shift_id:
            raise NoShiftForRegistrationException
        db_user = await self.__user_repository.get_by_telegram_id(new_user_data.telegram_id)
        if db_user:
            request = await self.__request_repository.get_by_user_and_shift(db_user.id, shift_id)
            if request:
                if request.status is Request.Status.PENDING:
                    db_user = await self.update_or_create_user(new_user_data, db_user)
                    raise RegistrationTakesTimeException
                if request.status is Request.Status.APPROVED:
                    raise AlreadyRegisteredException
                if request.status is Request.Status.DECLINED:
                    db_user = await self.update_or_create_user(new_user_data, db_user)
                    request.status = Request.Status.PENDING
                    await self.__request_repository.update(request.id, request)
                    raise RegistrationTakesTimeException
        db_user = await self.update_or_create_user(new_user_data, db_user)
        request = Request(user_id=db_user.id, shift_id=shift_id, status=Request.Status.PENDING)
        await self.__request_repository.create(request)
        raise RegistrationTakesTimeException

    async def update_or_create_user(self, user_scheme: UserCreateRequest, db_user: Optional[User] = None) -> User:
        """Обновить юзера или создать."""
        user = User(**user_scheme.dict())
        user.status = User.Status.PENDING
        if db_user:
            validate_date_of_birth(user.date_of_birth)
            return await self.__user_repository.update(db_user.id, user)
        await validate_user_create(user_scheme, self.__user_repository)
        return await self.__user_repository.create(user)

    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
        """Получить участника проекта по его telegram_id."""
        return await self.__user_repository.get_by_telegram_id(telegram_id)

    async def list_all_users(
        self,
        status: Optional[User.Status] = None,
        field_sort: Optional[UserFieldSortRequest] = None,
        direction_sort: Optional[UserDescAscSortRequest] = None,
    ) -> list[UserWithStatusResponse]:
        return await self.__user_repository.get_users_with_status(status, field_sort, direction_sort)
