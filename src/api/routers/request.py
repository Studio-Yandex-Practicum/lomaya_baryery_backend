from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_restful.cbv import cbv
from pydantic.schema import UUID

from src.api.request_models.request import RequestStatusUpdateRequest
from src.api.response_models.request import RequestResponse
from src.core.services.request_sevice import RequestService

router = APIRouter(prefix="/requests", tags=["Request"])


@cbv(router)
class RequestCBV:
    request_service: RequestService = Depends()

    @router.patch(
        "/{request_id}",
        response_model=RequestResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Обновить статус заявки",
        response_description="Информация по заявке",
    )
    async def update_request_status(
        self,
        request_id: UUID,
        new_status_data: RequestStatusUpdateRequest,
    ) -> RequestResponse:
        """Обновить статус заявки.

        - **status**: статус заявки
        """
        updated_request = await self.request_service.status_update(request_id, new_status_data)
        return RequestResponse(
            request_id=updated_request.id,
            user_id=updated_request.user.id,
            status=updated_request.status,
            **jsonable_encoder(updated_request.user)
        )
