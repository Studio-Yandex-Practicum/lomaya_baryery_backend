from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi_restful.cbv import cbv
from pydantic.schema import UUID

from src.api.request_models.request import RequestDeclineRequest
from src.api.response_models.request import RequestResponse
from src.core.services.request_sevice import RequestService

router = APIRouter(prefix="/requests", tags=["Request"])


@cbv(router)
class RequestCBV:
    request_service: RequestService = Depends()

    @router.patch(
        "/{request_id}/approve",
        response_model=RequestResponse,
        status_code=HTTPStatus.OK,
        summary="Одобрить заявку на участие.",
    )
    async def approve_request_status(
        self,
        request_id: UUID,
        request: Request,
    ) -> RequestResponse:
        """Одобрить заявку на участие в акции."""
        return await self.request_service.approve_request(request_id, request.app.state.bot_instance.bot)

    @router.patch(
        "/{request_id}/decline",
        response_model=RequestResponse,
        status_code=HTTPStatus.OK,
        summary="Отклонить заявку на участие.",
    )
    async def decline_request_status(
        self,
        request_id: UUID,
        decline_request_data: RequestDeclineRequest,
        request: Request,
    ) -> RequestResponse:
        """Отклонить заявку на участие в акции."""
        return await self.request_service.decline_request(
            request_id, request.app.state.bot_instance.bot, decline_request_data
        )
