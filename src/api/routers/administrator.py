from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv

from src.api.request_models.administrator import AdministratorAuthenticateRequest
from src.api.response_models.administrator import AdministratorResponse, TokenResponse
from src.core.db.models import Administrator
from src.core.services.administrator_service import (
    AdministratorService,
    get_current_active_administrator,
)

router = APIRouter(prefix="/administrators", tags=["Administrator"])


@cbv(router)
class AdministratorCBV:
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
        return await self.administrator_service.get_access_and_refresh_tokens(auth_data)

    @router.get(
        "/me",
        response_model=AdministratorResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Информация об администраторе",
        response_description="Информация о теущем активном администраторе",
    )
    async def get_me(self, current_active_admin: Administrator = Depends(get_current_active_administrator)):
        """Получить информацию о текущем  активном администраторе."""
        return current_active_admin
