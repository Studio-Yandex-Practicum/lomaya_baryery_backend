from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv

from src.api.request_models.administrator import (
    AdministratorAuthenticateRequest,
    AdministratorRegistrationRequest,
)
from src.api.response_models.administrator import AdministratorResponse, TokenResponse
from src.core.services.administrator_service import AdministratorService
from src.core.services.authentication_service import (
    OAUTH2_SCHEME,
    AuthenticationService,
)

router = APIRouter(prefix="/administrators", tags=["Administrator"])


@cbv(router)
class AdministratorCBV:
    authentication_service: AuthenticationService = Depends()
    administrator_service: AdministratorService = Depends()

    @router.post(
        "/login",
        response_model=TokenResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Аутентификация",
        response_description="Access и refresh токены.",
    )
    async def login(self, auth_data: AdministratorAuthenticateRequest) -> TokenResponse:
        """Аутентифицировать администратора по email и паролю.

        - **email**: электронная почта
        - **password**: пароль
        """
        return await self.authentication_service.login(auth_data)

    @router.get(
        "/me",
        response_model=AdministratorResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Информация об администраторе",
        response_description="Информация о теущем активном администраторе",
    )
    async def get_me(self, token: str = Depends(OAUTH2_SCHEME)):
        """Получить информацию о текущем  активном администраторе."""
        return await self.authentication_service.get_current_active_administrator(token)

    @router.post(
        '/register',
        response_model=AdministratorResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.CREATED,
        summary="Регистрация администратора",
        response_description="Регистрация нового администратора по токену приглашения.",
    )
    async def register_new_administrator(self, token: UUID, schema: AdministratorRegistrationRequest):
        """Зарегистрировать нового администратора по токену из приглашения."""
        return await self.administrator_service.register_new(token, schema)
