from fastapi import Depends

from src.api.request_models.request import GetListAllShiftRequests
from src.api.response_models.request import RequestDBRespone
from src.core.db.repository import RequestRepository


class RequestService:
    def __init__(self, request_repository: RequestRepository = Depends()) -> None:
        self.request_repository = request_repository

    async def list_all_requests(
        self,
        request_status_and_shift_id: GetListAllShiftRequests,
    ) -> list[RequestDBRespone]:
        return await self.request_repository.list_all_requests(request_status_and_shift_id)
