from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_restful.cbv import cbv

from src.api.request_models.user import UserDescAscSortRequest, UserFieldSortRequest
from src.api.response_models.error import generate_error_responses
from src.api.response_models.user import UserDetailResponse, UserWithStatusResponse
from src.core.db.models import User
from src.core.services.authentication_service import AuthenticationService
from src.core.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@cbv(router)
class UserCBV:
    user_service: UserService = Depends()
    authentication_service: AuthenticationService = Depends()
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer())

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
        field_sort: Optional[UserFieldSortRequest] = None,
        direction_sort: Optional[UserDescAscSortRequest] = None,
    ) -> list[UserWithStatusResponse]:
        """
        Получить список пользователей с фильтрацией по статусу.

        - **id**: id пользователя
        - **name**: имя пользователя
        - **surname**: фамилия пользователя
        - **date_of_birth**: день рождения пользователя
        - **city**: город пользователя
        - **phone_number**: телефон пользователя
        - **status**: статус пользователя
        - **shifts_count**: количество пройденных пользователем смен
        - **is_in_active_shift**: флаг, является ли пользователь участником текущей активной смены
        """
        await self.authentication_service.check_administrator_by_token(self.token)
        return await self.user_service.list_all_users(status, field_sort, direction_sort)

    @router.get(
        "/{user_id}",
        response_model=UserDetailResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Получить детальную информацию о пользователе",
        response_description="Детальная информация о пользователе",
        responses=generate_error_responses(HTTPStatus.NOT_FOUND),
    )
    async def get_user_detail(self, user_id: UUID) -> UserDetailResponse:
        """
        Получить детальную информацию о пользователе.

        - **id**: id пользователя
        - **name**: имя пользователя
        - **surname**: фамилия пользователя
        - **date_of_birth**: день рождения пользователя
        - **city**: город пользователя
        - **phone_number**: телефон пользователя
        - **shifts**: список смен пользователя
        """
        await self.authentication_service.check_administrator_by_token(self.token)
        return await self.user_service.get_user_by_id_with_shifts_detail(user_id)
