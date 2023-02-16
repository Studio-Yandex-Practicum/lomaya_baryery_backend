from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv

from src.api.error_templates import (
    ERROR_TEMPLATE_FOR_400,
    ERROR_TEMPLATE_FOR_401,
    ERROR_TEMPLATE_FOR_403,
    ERROR_TEMPLATE_FOR_422,
)
from src.api.request_models.administrator import (
    AdministratorAuthenticateRequest,
    AdministratorRegistrationRequest,
)
from src.api.response_models.administrator import AdministratorResponse, TokenResponse
from src.core.db.models import Administrator
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

    @router.post(
        '/register/{token}',
        response_model=AdministratorResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.CREATED,
        summary="Регистрация администратора",
        response_description="Регистрация нового администратора по токену приглашения.",
        responses={400: ERROR_TEMPLATE_FOR_400, 422: ERROR_TEMPLATE_FOR_422},
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
