from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from pydantic.schema import UUID

from src.api.request_models.request import Status
from src.api.response_models.request import RequestResponse
from src.core.services.request_sevice import RequestService

router = APIRouter(prefix="/requests", tags=["Request"])


@cbv(router)
class RequestCBV:
    request_service: RequestService = Depends()

    @router.patch(
        "/{request_id}/accept",
        status_code=HTTPStatus.OK,
        summary="Одобрить заявку на участие.",
    )
    async def approve_request_status(
        self,
        request_id: UUID,
    ) -> RequestResponse:
        """Одобрить заявку на участие в акции."""
        return await self.request_service.status_update(request_id, Status.APPROVED)

    @router.patch(
        "/{request_id}/decline",
        status_code=HTTPStatus.OK,
        summary="Отклонить заявку на участие.",
    )
    async def decline_request_status(
        self,
        request_id: UUID,
    ) -> RequestResponse:
        """Отклонить заявку на участие в акции."""
        return await self.request_service.status_update(request_id, Status.DECLINED)
