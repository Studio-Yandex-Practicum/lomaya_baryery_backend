from fastapi import APIRouter, Depends

from src.api.request_models.request import GetListAllShiftRequests
from src.api.response_models.request import RequestDBRespone
from src.core.services.request_service import RequestService

router = APIRouter(prefix="/requests", tags=["requests"])


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
