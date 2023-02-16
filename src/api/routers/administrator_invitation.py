from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi_restful.cbv import cbv

from src.api.error_templates import ERROR_TEMPLATE_FOR_400, ERROR_TEMPLATE_FOR_422
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
        '/invite',
        response_model=None,
        status_code=HTTPStatus.CREATED,
        summary="Создать и отправить на электронную почту ссылку для регистрации нового администратора/психолога",
    )
    async def create_and_send_invitation(
        self, request: Request, invitation_data: AdministratorInvitationRequest
    ) -> None:
        invite = await self.administrator_invitation_service.create_mail_request(invitation_data)
        url = f"{request.url.scheme}://{request.client.host}:{request.url.port}/administrators/register/{invite.token}"
        await self.email_provider.send_invitation_link(url, invite.name, invite.email)

    @router.get(
        '/register/{token}',
        response_model=AdministratorInvitationResponse,
        status_code=HTTPStatus.OK,
        summary="Получить данные приглашенного администратора по токену.",
        responses={
            400: ERROR_TEMPLATE_FOR_400,
            422: ERROR_TEMPLATE_FOR_422,
        },
    )
    async def get_invitation_by_token(self, token: UUID) -> AdministratorInvitationResponse:
        """
        Получить информацию о приглашенном администраторе по токену.

        - **name**: имя администратора
        - **surname**: фамилия администратора
        - **email**: адрес электронной почты
        """
        return await self.administrator_invitation_service.get_invitation_by_token(token)
