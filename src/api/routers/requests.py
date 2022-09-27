from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db.db import get_session
from src.core.services.request_service import RequestService
from src.api.request_models.request import RequestList
from src.api.response_models.request import RequestDB

router = APIRouter()


@router.post(
    '/',
    response_model=list[RequestDB],
    response_model_exclude_none=True
)
async def get_list_all_requests_on_project(
    requset_list: RequestList,
    session: AsyncSession = Depends(get_session)
):
    """
    Данный метод будет использоваться для получения сведений
    обо всех заявках смены с возможностью фильтрации по:
    номеру смены и статусу заявки.
    """
    return await RequestService.list_all_requests(
        list_request=requset_list,
        session=session
    )
