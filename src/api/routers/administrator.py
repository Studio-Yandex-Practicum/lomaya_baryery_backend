from http import HTTPStatus
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_restful.cbv import cbv

from src.api.request_models.administrator import (
    AdministratorAuthenticateRequest,
    AdministratorRegistrationRequest,
)
from src.api.response_models.administrator import (
    AdministratorAndAccessTokenResponse,
    AdministratorResponse,
)
from src.api.response_models.error import generate_error_responses
from src.core import exceptions
from src.core.db.models import Administrator
from src.core.services.administrator_service import AdministratorService
from src.core.services.authentication_service import AuthenticationService

router = APIRouter(prefix="/administrators", tags=["Administrator"])


@cbv(router)
class AdministratorCBV:
    authentication_service: AuthenticationService = Depends()
    administrator_service: AdministratorService = Depends()

    @router.post(
        "/login",
        response_model=AdministratorAndAccessTokenResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Аутентификация",
        response_description="Access-токен и информация о пользователе.",
        responses=generate_error_responses(HTTPStatus.BAD_REQUEST, HTTPStatus.FORBIDDEN),
    )
    async def login(
        self, response: Response, auth_data: AdministratorAuthenticateRequest
    ) -> AdministratorAndAccessTokenResponse:
        """Аутентифицировать администратора по email и паролю. Вернуть access-токен и информацию об администраторе.

        - **email**: электронная почта
        - **password**: пароль
        """
        admin_and_token = await self.authentication_service.login(auth_data)
        response.set_cookie(key="refresh_token", value=admin_and_token.refresh_token, httponly=True, samesite="strict")
        admin_and_token.administrator.access_token = admin_and_token.access_token
        return admin_and_token.administrator

    @router.get(
        "/refresh",
        response_model=AdministratorAndAccessTokenResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Обновление аутентификационного токена.",
        response_description="Access-токен и информация о пользователе.",
    )
    async def refresh(
        self, response: Response, refresh_token: str | None = Cookie(default=None)
    ) -> AdministratorAndAccessTokenResponse:
        """Обновление access и refresh токенов при помощи refresh токена, получаемого из cookie.

        Вернуть access-токен и информацию об администраторе.
        """
        if not refresh_token:
            raise exceptions.UnauthorizedError()
        admin_and_token = await self.authentication_service.refresh(refresh_token)
        response.set_cookie(key="refresh_token", value=admin_and_token.refresh_token, httponly=True, samesite="strict")
        admin_and_token.administrator.access_token = admin_and_token.access_token
        return admin_and_token.administrator

    @router.get(
        "/me",
        response_model=AdministratorResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Информация об администраторе",
        response_description="Информация о текущем активном администраторе",
        responses=generate_error_responses(HTTPStatus.BAD_REQUEST, HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN),
    )
    async def get_me(self, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """Получить информацию о текущем активном администраторе."""
        return await self.authentication_service.get_current_active_administrator(token.credentials)

    @router.post(
        '/register/{token}',
        response_model=AdministratorResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.CREATED,
        summary="Регистрация администратора",
        response_description="Регистрация нового администратора по токену приглашения.",
        responses=generate_error_responses(HTTPStatus.BAD_REQUEST, HTTPStatus.UNPROCESSABLE_ENTITY),
    )
    async def register_new_administrator(self, token: UUID, schema: AdministratorRegistrationRequest) -> Any:
        """Зарегистрировать нового администратора по токену из приглашения.

        - **name**: Имя
        - **surname**: Фамилия
        - **password**: Пароль администратора
        """
        return await self.administrator_service.register_new_administrator(token, schema)

    @router.get(
        "/",
        response_model=list[AdministratorResponse],
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Запрос списка администраторов с возможностью фильтрации по статусу и роли",
        response_description="Список администраторов",
    )
    async def get_administrators(
        self,
        status: Administrator.Status = None,
        role: Administrator.Role = None,
    ) -> Any:
        """Получить список администраторов с опциональной фильтрацией по статусу и роли.

        Аргументы:
            status (Administrator.Status, optional): Требуемый статус администраторов. По-умолчанию None.
            role (Administrator.Role, optional): Требуемая роль администраторов. По-умолчанию None.
        """
        return await self.administrator_service.get_administrators_filter_by_role_and_status(status, role)
