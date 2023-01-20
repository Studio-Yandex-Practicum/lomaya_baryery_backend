from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi_restful.cbv import cbv

from src.api.request_models.administrator_mail_request import (
    AdministratorMailRequestRequest,
)
from src.core.email import EmailProvider
from src.core.services.administrator_mail_request import AdministratorMailRequestService

router = APIRouter(prefix="/administrators", tags=["Administrator"])


@cbv(router)
class AdministratorCBV:
    administrator_mail_request_service: AdministratorMailRequestService = Depends()

    @router.post(
        '/invite',
        response_model=None,
        status_code=HTTPStatus.CREATED,
        summary="Создать и отправить на электронную почту ссылку для регистрации нового администратора/психолога",
    )
    async def send_invite(self, request: Request, invitation_data: AdministratorMailRequestRequest) -> None:
        invite = await self.administrator_mail_request_service.create_mail_request(invitation_data)
        url = f"{request.url.scheme}://{request.client.host}:{request.url.port}/administrators/register/{invite.id}"
        await EmailProvider().send_invitation_link(url, invite.name, invite.email)
