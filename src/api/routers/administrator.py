from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_restful.cbv import cbv

from src.api.request_models.administrator import (
    AdministratorAuthenticateRequest,
    AdministratorPasswordResetRequest,
    AdministratorPasswordSaveRequest,
    AdministratorRegistrationRequest,
)
from src.api.response_models.administrator import AdministratorResponse, TokenResponse
from src.api.response_models.error import generate_error_responses
from src.core.db.models import Administrator
from src.core.email import EmailProvider
from src.core.services.administrator_service import AdministratorService
from src.core.services.authentication_service import AuthenticationService

router = APIRouter(prefix="/administrators", tags=["Administrator"])


@cbv(router)
class AdministratorCBV:
    authentication_service: AuthenticationService = Depends()
    administrator_service: AdministratorService = Depends()
    email: EmailProvider = Depends()

    @router.post(
        "/login",
        response_model=TokenResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Аутентификация",
        response_description="Access и refresh токены.",
        responses=generate_error_responses(HTTPStatus.BAD_REQUEST, HTTPStatus.FORBIDDEN),
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

    @router.post(
        "/password_reset",
        status_code=HTTPStatus.OK,
        summary="Восстановление пароля",
        response_description="email пользователя.",
        responses=generate_error_responses(HTTPStatus.BAD_REQUEST, HTTPStatus.FORBIDDEN),
    )
    async def password_reset(self, request_data: AdministratorPasswordResetRequest) -> None:
        """Восстановление пароля администратора по email."""
        await self.administrator_service.get_by_email(request_data.email)
        administrator_password_reset = await self.administrator_service.create_password_reset_object(request_data.email)
        return await self.email.send_reset_password_message(
            email=administrator_password_reset.email, token=administrator_password_reset.token
        )

    @router.get(
        '/password_reset/{token}',
        status_code=HTTPStatus.OK,
        summary='Введите новый пароль пароля',
        response_description='Новый пароль.',
        response_class=HTMLResponse,
        responses=generate_error_responses(HTTPStatus.BAD_REQUEST, HTTPStatus.FORBIDDEN),
    )
    async def change_password(self, request: Request, token: str) -> None:
        """URL для отправки пользователю формы восстановления пароля."""
        return await self.administrator_service.send_restore_form(request, token)

    @router.post(
        '/password_reset/{token}',
        status_code=HTTPStatus.OK,
        summary='Введите новый пароль пароля',
        response_description='Новый пароль.',
        responses=generate_error_responses(HTTPStatus.BAD_REQUEST, HTTPStatus.FORBIDDEN),
    )
    async def save_password(self, data: AdministratorPasswordSaveRequest) -> None:
        """Запись нового пароля в БД."""
        return await self.administrator_service.save_new_password(data.token, data.password)
