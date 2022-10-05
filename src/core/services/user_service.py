from fastapi import Depends

from src.api.request_models.user import RequestCreateRequest, UserCreateRequest
from src.core.db.models import Request, User
from src.core.db.repository.request_repository import RequestRepository
from src.core.db.repository.user_repository import UserRepository


class RegistrationService:
    def __init__(
        self, user_repository: UserRepository = Depends(), request_repository: RequestRepository = Depends()
    ) -> None:
        self.user_repository = user_repository
        self.request_repository = request_repository

    async def user_registration(self, user_data: dict):
        """Регистрация пользователя. Отправка запроса на участие в смене."""
        telegram_id = user_data.get("telegram_id")
        user = await self.user_repository.get_by_attribute("telegram_id", telegram_id)
        if not user:
            user_scheme = UserCreateRequest(**user_data)
            user = User(**user_scheme.dict())
            await self.user_repository.create(user)
        request = await self.request_repository.get_by_attribute("id", user.id)
        if not request:
            request_scheme = RequestCreateRequest(user_id=user.id, status=Request.Status.PENDING)
            request = Request(**request_scheme.dict())
            await self.user_repository.create(request)
