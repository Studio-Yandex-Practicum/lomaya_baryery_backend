from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from pydantic.schema import UUID

from src.api.request_models.request import (
    GetListAllShiftRequests,
    RequestStatusUpdateRequest,
)
from src.api.response_models.request import RequestDBRespone, RequestResponse
from src.core.services.request_sevice import RequestService

router = APIRouter(prefix="/requests", tags=["Request"])


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
    new_status_data: RequestStatusUpdateRequest,
    request_service: RequestService = Depends(),
) -> RequestResponse:
    """Обновить статус заявки.

    - **request_id**: id заявки
    - **user_id**: id пользователя
    - **name**: имя пользователя
    - **surname**: фамилия пользователя
    - **date_of_birth**: дата рождения пользователя
    - **city**: город пользователя
    - **phone_number**: телефонный номер пользователя
    - **status**: статус заявки
    """
    updated_request = await request_service.status_update(request_id, new_status_data)
    return RequestResponse(
        request_id=updated_request.id,
        user_id=updated_request.user.id,
        status=updated_request.status,
        **jsonable_encoder(updated_request.user)
    )


@router.post(
    '/',
    response_model=list[RequestDBRespone],
    response_model_exclude_none=True,
    summary=("Получить информацию обо всех заявках смены"
             "с возможностью фильтрации"),
    response_description="Полная информация обо заявках смены.",
)
async def get_list_all_requests_on_project(
    request_data: GetListAllShiftRequests,
    request_service: RequestService = Depends(),
) -> RequestDBRespone:
    """
    Данный метод будет использоваться для получения сведений
    обо всех заявках смены с возможностью фильтрации по:
    номеру смены и статусу заявки.
    - **user_id**: Номер пользователя
    - **name**: Имя пользователя
    - **surname**: Фамилия пользователя
    - **date_of_birth**: Дата рождения пользователя
    - **city**: Город пользователя
    - **phone**: Телефон пользователя
    - **request_id**: Номер заявки
    - **status**: Статус заявки
    """
    return await request_service.list_all_requests(
        request_status_and_shift_id=request_data,
    )
