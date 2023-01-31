from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv

from src.api.request_models.administrator import AdministratorAuthenticateRequest
from src.api.response_models.administrator import AdministratorResponse, TokenResponse
from src.api.response_models.shift import ErrorResponse
from src.core.services.authentication_service import (
    OAUTH2_SCHEME,
    AuthenticationService,
)

router = APIRouter(prefix="/administrators", tags=["Administrator"])


ERROR_TEMPLATE_FOR_400 = {"description": "Bad Request Response", "model": ErrorResponse}
ERROR_TEMPLATE_FOR_401 = {"description": "Unauthorized", "model": ErrorResponse}
ERROR_TEMPLATE_FOR_403 = {"description": "Forbidden Response", "model": ErrorResponse}


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
        responses={
            400: ERROR_TEMPLATE_FOR_400,
            403: ERROR_TEMPLATE_FOR_403,
        },
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
        responses={
            400: ERROR_TEMPLATE_FOR_400,
            401: ERROR_TEMPLATE_FOR_401,
            403: ERROR_TEMPLATE_FOR_403,
        },
    )
    async def get_me(self, token: str = Depends(OAUTH2_SCHEME)):
        """Получить информацию о текущем  активном администраторе."""
        return await self.authentication_service.get_current_active_administrator(token)
