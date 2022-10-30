from http import HTTPStatus

from fastapi import Depends, HTTPException
from pydantic.schema import UUID

from src.api.request_models.request import RequestStatusUpdateRequest
from src.bot.services import BotService as bot_services
from src.core.db.models import Request
from src.core.db.repository import RequestRepository

REVIEWED_REQUEST = "Заявка была обработана, статус заявки: {}."


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
        """Обновление статус заявки."""
        request = await self.check_request_status(request_id)
        request.status = new_status_data
        return await self.request_repository.update(request.id, request)

    async def check_request_status(self, id: UUID) -> None:
        """Уточнение статуса заявки."""
        request = await self.get_request(id)
        if request.status in (Request.Status.APPROVED, Request.Status.DECLINED):
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=REVIEWED_REQUEST.format(request.status))

        return request

    async def accepted_request_update_status(self, id: UUID) -> Request:
        """Заявка на участие одобрена.

        - Уточнение текущего статуса заявки.
        - Обновление статуса заявки.
        - Уведомление участника об одобрении заявки.
        """
        request = await self.status_update(id, Request.Status.APPROVED)
        await bot_services().notify_approved_request(request.user)
        return request

    async def declined_request_update_status(self, id: UUID) -> Request:
        """Заявка на участие отклонена.

        - Уточнение текущего статуса заявки.
        - Обновление статуса заявки.
        - Уведомление участника об отклонении заявки.
        """
        request = await self.status_update(id, Request.Status.DECLINED)
        await bot_services().notify_declined_request(request.user)
        return request

    async def get_approved_shift_user_ids(self, shift_id: UUID) -> list[UUID]:
        """Получить id одобренных участников смены."""
        return await self.request_repository.get_shift_user_ids(shift_id)
