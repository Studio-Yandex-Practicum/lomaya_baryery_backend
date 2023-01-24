from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi_restful.cbv import cbv

from src.api.request_models.administrator_invitation import (
    AdministratorInvitationRequest,
)
from src.core.email import EmailProvider
from src.core.services.administrator_invitation import AdministratorInvitationService

router = APIRouter(prefix="/administrators", tags=["Administrator"])


@cbv(router)
class AdministratorInvitationCBV:
    administrator_invitation_service: AdministratorInvitationService = Depends()
    email_provider: EmailProvider = Depends()

    @router.post(
        '/invite',
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
