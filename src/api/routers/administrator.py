from http import HTTPStatus
from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_restful.cbv import cbv

from src.api.request_models.administrator import (
    AdministratorAuthenticateRequest,
    AdministratorRegistrationRequest,
    RefreshToken,
)
from src.api.response_models.administrator import AdministratorResponse, TokenResponse
from src.api.response_models.error import generate_error_responses
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
        response_model=dict[str, Union[TokenResponse, AdministratorResponse]],
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Аутентификация",
        response_description="Access-токен и информация о пользователе.",
        responses=generate_error_responses(HTTPStatus.BAD_REQUEST, HTTPStatus.FORBIDDEN),
    )
    async def login(
        self, response: Response, auth_data: AdministratorAuthenticateRequest
    ) -> dict[str, Union[TokenResponse, AdministratorResponse]]:
        """Аутентифицировать администратора по email и паролю. Вернуть access-токен и информацию об администраторе.

        - **email**: электронная почта
        - **password**: пароль
        """
        tokens = await self.authentication_service.login(auth_data)
        administrator = await self.authentication_service._AuthenticationService__authenticate_administrator(auth_data)
        response.set_cookie(key="refresh_token", value=tokens.refresh_token, httponly=True, samesite="strict")
        tokens.refresh_token = None
        return {"access": tokens, "administrator": administrator}

    @router.post(
        "/refresh",
        response_model=dict[str, Union[TokenResponse, AdministratorResponse]],
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Обновление аутентификационного токена.",
        response_description="Access-токен и информация о пользователе.",
    )
    async def refresh(
        self, response: Response, request_data: RefreshToken
    ) -> dict[str, Union[TokenResponse, AdministratorResponse]]:
        """Обновление access и refresh токенов при помощи refresh токена.

        Вернуть access-токен и информацию об администраторе.
        """
        tokens = await self.authentication_service.refresh(request_data.refresh_token)
        response.set_cookie(key="refresh_token", value=tokens.refresh_token, httponly=True, samesite="strict")
        tokens.refresh_token = None
        administrator = await self.authentication_service.get_current_active_administrator(tokens.access_token)
        return {"access": tokens, "administrator": administrator}

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
    async def register_new_administrator(
        self, token: UUID, schema: AdministratorRegistrationRequest
    ) -> AdministratorResponse:
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
    ) -> list[AdministratorResponse]:
        """Получить список администраторов с опциональной фильтрацией по статусу и роли.

        Аргументы:
            status (Administrator.Status, optional): Требуемый статус администраторов. По-умолчанию None.
            role (Administrator.Role, optional): Требуемая роль администраторов. По-умолчанию None.
        """
        return await self.administrator_service.get_administrators_filter_by_role_and_status(status, role)
