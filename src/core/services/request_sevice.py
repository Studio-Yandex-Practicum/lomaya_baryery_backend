from fastapi import Depends
from pydantic.schema import UUID

from src.api.request_models.request import RequestStatusUpdate
from src.core.db.models import Request
from src.core.db.repository import RequestRepository


class RequestService:
    def __init__(self, request_repository: RequestRepository = Depends()) -> None:
        self.request_repository = request_repository

    async def get_request(
        self,
        request_id: UUID,
    ) -> Request:
        """Получить объект заявку по id."""
        return await self.request_repository.get(request_id)

    async def status_update(self, request: Request, new_status_data: RequestStatusUpdate) -> Request:
        """Обновить статус заявки."""
        setattr(request, "status", new_status_data.status)
        return await self.request_repository.update(id=request.id, request=request)
