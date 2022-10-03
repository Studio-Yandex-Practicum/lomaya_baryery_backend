from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from pydantic.schema import UUID

from src.api.request_models.request import RequestStatusUpdate, Status
from src.api.response_models.request import RequestResponse
from src.bot.services import send_approval_callback, send_rejection_callback
from src.core.services.request_sevice import RequestService

router = APIRouter(prefix="/request", tags=["Request"])


@router.patch(
    "/{request_id}",
    response_model=RequestResponse,
    response_model_exclude_none=True,
    status_code=HTTPStatus.OK,
    summary="Обновить статус заявки",
    response_description="Информация по заявке",
)
async def update_request_status(
    request_id: UUID,
    new_status_data: RequestStatusUpdate,
    request_service: RequestService = Depends(),
) -> RequestResponse:
    request = await request_service.get_request(request_id)
    updated_request = await request_service.status_update(request, new_status_data)
    if updated_request.status is Status.APPROVED:
        await send_approval_callback(updated_request.user)
    else:
        await send_rejection_callback(updated_request.user)
    request_and_user_data = {**jsonable_encoder(updated_request), **jsonable_encoder(updated_request.user)}
    data_for_response = dict()
    for field in request_and_user_data:
        if field in RequestResponse.__fields__:
            data_for_response[field] = request_and_user_data[field]
    return RequestResponse(request_id=updated_request.id, **data_for_response)
