from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv

from src.api.request_models.administrator import (
    AdministratorAuthenticateRequest,
    AdministratorCreateRequest,
)
from src.api.response_models.administrator import AdministratorResponse, TokenResponse
from src.core.services.administrator_service import AdministratorService

router = APIRouter(prefix="/administrators", tags=["Administrator"])


@cbv(router)
class AdministratorCBV:
    administrator_service: AdministratorService = Depends()

    @router.post(
        "/",
        response_model=AdministratorResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.CREATED,
        summary="Создать нового администратора",
        response_description="Информация о созданном администраторе",
    )
    async def create_new_administrator(self, administrator: AdministratorCreateRequest) -> AdministratorResponse:
        """Создать администратора.

        - **name**: имя администратора
        - **surname**: фамилия администратора
        - **email**: электронная почта
        - **password**: пароль
        """
        return await self.administrator_service.create_new_administrator(administrator)

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
        return await self.administrator_service.get_access_and_refresh_tokens(auth_data)
