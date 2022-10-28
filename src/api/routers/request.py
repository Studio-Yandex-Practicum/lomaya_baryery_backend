from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_restful.cbv import cbv
from pydantic.schema import UUID

from src.api.response_models.request import RequestResponse
from src.core.services.request_sevice import RequestService

router = APIRouter(prefix="/requests", tags=["Request"])


@cbv(router)
class RequestCBV:
    request_service: RequestService = Depends()

    @router.patch(
        "/{request_id}/accept",
        response_model=RequestResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Одобрить заявку на участие.",
        response_description="Информация по заявке",
    )
    async def accept_request_status(
        self,
        request_id: UUID,
    ) -> RequestResponse:
        """Одобрить заявку на участие в акции."""
        updated_request = await self.request_service.accepted_request_update_status(request_id)
        return RequestResponse(
            request_id=updated_request.id,
            user_id=updated_request.user.id,
            status=updated_request.status,
            **jsonable_encoder(updated_request.user)
        )

    @router.patch(
        "/{request_id}/decline",
        response_model=RequestResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Отклонить заявку на участие.",
        response_description="Информация по заявке",
    )
    async def decline_request_status(
        self,
        request_id: UUID,
    ) -> RequestResponse:
        """Отклонить заявку на участие в акции."""
        updated_request = await self.request_service.declined_request_update_status(request_id)
        return RequestResponse(
            request_id=updated_request.id,
            user_id=updated_request.user.id,
            status=updated_request.status,
            **jsonable_encoder(updated_request.user)
        )
