from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv

from src.api.request_models.administrator import AdministratorAuthenticateRequest
from src.api.response_models.administrator import AdministratorResponse, TokenResponse
from src.core.services.authentication_service import (
    OAUTH2_SCHEME,
    AuthenticationService,
)

router = APIRouter(prefix="/administrators", tags=["Administrator"])


@cbv(router)
class AdministratorCBV:
    authentication_service: AuthenticationService = Depends()

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
