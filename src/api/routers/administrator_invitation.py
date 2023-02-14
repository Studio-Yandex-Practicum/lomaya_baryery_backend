from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi_restful.cbv import cbv

from src.api.request_models.administrator_invitation import (
    AdministratorInvitationRequest,
)
from src.api.response_models.administrator_invitation import (
    AdministratorInvitationResponse,
)
from src.core.email import EmailProvider
from src.core.services.administrator_invitation import AdministratorInvitationService

router = APIRouter(prefix="/administrators", tags=["Administrator"])


@cbv(router)
class AdministratorInvitationCBV:
    administrator_invitation_service: AdministratorInvitationService = Depends()
    email_provider: EmailProvider = Depends()

    @router.post(
        '/invitations',
        response_model=None,
        status_code=HTTPStatus.CREATED,
        summary="Создать и отправить на электронную почту ссылку для регистрации нового администратора/психолога",
    )
    async def create_and_send_invitation(
        self, request: Request, invitation_data: AdministratorInvitationRequest
    ) -> None:
        invite = await self.administrator_invitation_service.create_mail_request(invitation_data)
        url = f"{request.url.scheme}://{request.client.host}:{request.url.port}/administrators/register/{invite.id}"
        await self.email_provider.send_invitation_link(url, invite.name, invite.email)

    @router.get(
        '/invitations',
        response_model=list[AdministratorInvitationResponse],
        status_code=HTTPStatus.OK,
        summary="Получить информацию о приглашениях, отправленных администраторам",
        response_description="Информация о приглашениях",
    )
    async def get_all_invitations(self) -> Any:
        return await self.administrator_invitation_service.list_all_invitations()
