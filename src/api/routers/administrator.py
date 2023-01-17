import hashlib
import secrets
from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi_restful.cbv import cbv

from src.api.request_models.administrator import AdministratorMailRequestRequest
from src.api.response_models.administrator import AdministratorMailRequestResponse
from src.core.services.administrator_mail_request import AdministratorMailRequestService

router = APIRouter(prefix="/administrators", tags=["Administrator"])


@cbv(router)
class AdministratorCBV:
    administrator_mail_request_service: AdministratorMailRequestService = Depends()

    @router.post(
        '/invite',
        response_model=AdministratorMailRequestResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.CREATED,
        summary="Создать ссылку для регистрации нового администратора",
        response_description="Ссылка для регистрации",
    )
    async def send_invite(
        self, request: Request, invitation_data: AdministratorMailRequestRequest
    ) -> AdministratorMailRequestResponse:
        key = secrets.token_bytes()
        token = hashlib.sha256(key).hexdigest()
        await self.administrator_mail_request_service.create_invite(invitation_data, token)
        # TODO Добавить отправку сообщения на электронную почту
        return AdministratorMailRequestResponse(url=request.url_for('process_invite', key=key.hex()))

    @router.get(
        '/invite/{key}',
    )
    async def process_invite(self, key: str):
        await self.administrator_mail_request_service.verify_token(key)
        pass
