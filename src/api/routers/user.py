from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv

from src.api.request_models.user import UserSortRequest
from src.api.response_models.user import UserWithStatusResponse
from src.core.db.models import User
from src.core.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["User"])


@cbv(router)
class UserCBV:
    user_service: UserService = Depends()

    @router.get(
        "/",
        response_model=list[UserWithStatusResponse],
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Получить список пользователей со статусом",
        response_description="Информация о пользователях с фильтрацией по статусу и возможностью сортировки",
    )
    async def get_all_users(
        self,
        status: Optional[User.Status] = None,
        sort: Optional[UserSortRequest] = None,
    ) -> list[UserWithStatusResponse]:
        """Получить список пользователей с фильтрацией по статусу.

        - **id**: id пользователя
        - **name**: имя пользователя
        - **surname**: фамилия пользователя
        - **date_of_birth**: день рождения пользователя
        - **city**: город пользователя
        - **phone_number**: телефон пользователя
        - **status**: статус пользователя
        """
        return await self.user_service.list_all_users(status, sort)
