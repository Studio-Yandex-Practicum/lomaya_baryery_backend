from http import HTTPStatus

from fastapi import Depends, HTTPException
from pydantic.schema import UUID

from src.api.request_models.request import RequestStatusUpdateRequest, Status
from src.bot.services import BotService
from src.core.db.models import Request
from src.core.db.repository import RequestRepository

REVIEWED_REQUEST = "Заявка была обработана, статус заявки: {}."


class RequestService:
    def __init__(self, request_repository: RequestRepository = Depends()) -> None:
        self.__request_repository = request_repository
        self.__bot_service = BotService()

    async def status_update(self, request_id: UUID, new_status_data: RequestStatusUpdateRequest) -> HTTPStatus.OK:
        """Обновление статуса заявки."""
        request = await self.__request_repository.get(request_id)
        if new_status_data is Status.APPROVED:
            return await self.approve_request(request)
        return await self.decline_request(request)

    async def approve_request(self, request: Request) -> HTTPStatus.OK:
        """Заявка одобрена. Уведомление участника в телеграм."""
        if request.status is Status.APPROVED:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=REVIEWED_REQUEST.format(request.status))
        request.status = Status.APPROVED
        await self.__request_repository.update(request.id, request)
        await self.__bot_service.notify_approved_request(request.user)
        return HTTPStatus.OK

    async def decline_request(self, request: Request) -> HTTPStatus.OK:
        """Заявка отклонена. Уведомление участника в телеграм."""
        if request.status is Status.DECLINED:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=REVIEWED_REQUEST.format(request.status))
        request.status = Status.DECLINED
        await self.__request_repository.update(request.id, request)
        await self.__bot_service.notify_declined_request(request.user)
        return HTTPStatus.OK

    async def get_approved_shift_user_ids(self, shift_id: UUID) -> list[UUID]:
        """Получить id одобренных участников смены."""
        return await self.__request_repository.get_shift_user_ids(shift_id)
