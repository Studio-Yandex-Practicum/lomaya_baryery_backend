from http import HTTPStatus

from fastapi import Depends, HTTPException
from pydantic.schema import UUID

from src.api.request_models.request import RequestStatusUpdateRequest, Status
from src.bot.services import send_approval_callback, send_rejection_callback
from src.core.db.models import Request, User
from src.core.db.repository.request_repository import RequestRepository

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
        await self.send_message(request.user, request.status)
        return await self.request_repository.update(id=request.id, request=request)

    async def send_message(self, user: User, status: str) -> None:
        """Отправить сообщение о решении по заявке в telegram."""
        if status is Status.APPROVED:
            return await send_approval_callback(user)
        return await send_rejection_callback(user)
