from http import HTTPStatus
from typing import Any
from urllib.parse import urljoin
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_restful.cbv import cbv

from src.api.request_models.administrator_invitation import (
    AdministratorInvitationRequest,
)
from src.api.response_models.administrator_invitation import (
    AdministratorInvitationResponse,
)
from src.api.response_models.error import generate_error_responses
from src.core.email import EmailProvider
from src.core.services.administrator_invitation import AdministratorInvitationService
from src.core.services.authentication_service import AuthenticationService
from src.core.settings import settings

router = APIRouter(prefix="/administrators", tags=["Administrator"])


@cbv(router)
class AdministratorInvitationCBV:
    administrator_invitation_service: AdministratorInvitationService = Depends()
    authentication_service: AuthenticationService = Depends()
    email_provider: EmailProvider = Depends()

    @router.post(
        '/invitations',
        response_model=AdministratorInvitationResponse,
        status_code=HTTPStatus.CREATED,
        responses=generate_error_responses(
            HTTPStatus.UNAUTHORIZED,
            HTTPStatus.NOT_FOUND,
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        summary="Создать и отправить на электронную почту ссылку для регистрации нового администратора/психолога",
    )
    async def create_and_send_invitation(
        self,
        request: Request,
        invitation_data: AdministratorInvitationRequest,
        token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    ) -> Any:
        await self.authentication_service.get_current_active_administrator(token.credentials)
        invite = await self.administrator_invitation_service.create_mail_request(invitation_data)
        url = urljoin(settings.APPLICATION_URL, f"/pwd_create/{invite.token}")
        await self.email_provider.send_invitation_link(url, invite.name, invite.email)
        return invite

    @router.get(
        '/invitations',
        response_model=list[AdministratorInvitationResponse],
        status_code=HTTPStatus.OK,
        responses=generate_error_responses(HTTPStatus.BAD_REQUEST, HTTPStatus.UNAUTHORIZED),
        summary="Получить информацию о приглашениях, отправленных администраторам",
        response_description="Информация о приглашениях",
    )
    async def get_all_invitations(
        self, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> list[AdministratorInvitationResponse]:
        await self.authentication_service.get_current_active_administrator(token.credentials)
        return await self.administrator_invitation_service.list_all_invitations()

    @router.get(
        '/register/{token}',
        response_model=AdministratorInvitationResponse,
        status_code=HTTPStatus.OK,
        summary="Получить данные приглашенного администратора по токену.",
        responses=generate_error_responses(HTTPStatus.BAD_REQUEST, HTTPStatus.UNPROCESSABLE_ENTITY),
    )
    async def get_invitation_by_token(self, token: UUID) -> AdministratorInvitationResponse:
        """
        Получить информацию о приглашенном администраторе по токену.

        - **name**: имя администратора
        - **surname**: фамилия администратора
        - **email**: адрес электронной почты
        """
        return await self.administrator_invitation_service.get_invitation_by_token(token)

    @router.patch(
        '/invitations/{invitation_id}/deactivate',
        status_code=HTTPStatus.OK,
        response_model=AdministratorInvitationResponse,
        responses=generate_error_responses(HTTPStatus.NOT_FOUND, HTTPStatus.BAD_REQUEST),
        summary="Деактивировать приглашение, отравленное администратору",
        response_description="Информация о приглашении",
    )
    async def deactivate_invitation(
        self, invitation_id: UUID, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> Any:
        await self.authentication_service.get_current_active_administrator(token.credentials)
        return await self.administrator_invitation_service.deactivate_invitation(invitation_id)

    @router.patch(
        '/invitations/{invitation_id}/reactivate',
        status_code=HTTPStatus.OK,
        response_model=AdministratorInvitationResponse,
        responses=generate_error_responses(HTTPStatus.NOT_FOUND, HTTPStatus.BAD_REQUEST),
        summary=(
            "Активировать приглашение повторно и отправить ссылку"
            "на почту для регистрации нового администратора/психолога"
        ),
        response_description="Информация о приглашении",
    )
    async def reactivate_invitation(
        self, invitation_id: UUID, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> Any:
        await self.authentication_service.get_current_active_administrator(token.credentials)
        invitation = await self.administrator_invitation_service.reactivate_invitation(invitation_id)
        url = urljoin(settings.APPLICATION_URL, f"/pwd_create/{invitation.token}")
        await self.email_provider.send_invitation_link(url, invitation.name, invitation.email)
        return invitation
