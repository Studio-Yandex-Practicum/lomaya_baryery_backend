from http import HTTPStatus

from fastapi import Depends, HTTPException
from pydantic.schema import UUID

from src.api.request_models.request import RequestStatusUpdateRequest
from src.bot.services import send_message_about_new_request_status
from src.core.db.models import Request
from src.core.db.repository import RequestRepository

REVIEWED_REQUEST = "Данная заявка уже была рассмотрена ранее"


class RequestService:
    def __init__(self, request_repository: RequestRepository = Depends()) -> None:
        self.request_repository = request_repository

    async def get_request(
        self,
        request_id: UUID,
    ) -> Request:
        """Получить объект заявку по id."""
        return await self.request_repository.get(request_id)

    async def status_update(self, request_id: UUID, new_status_data: RequestStatusUpdateRequest) -> Request:
        """Обновить статус заявки."""
        request = await self.get_request(request_id)
        if request.status == new_status_data.status:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=REVIEWED_REQUEST)
        request.status = new_status_data.status
        await send_message_about_new_request_status(request.user, request.status)
        return await self.request_repository.update(id=request.id, request=request)

    async def get_approved_shift_user_ids(self, shift_id: UUID) -> list[UUID]:
        """Получить id одобренных участников смены."""
        return await self.request_repository.get_shift_user_ids(shift_id)
