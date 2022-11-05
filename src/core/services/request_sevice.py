from http import HTTPStatus

from fastapi import HTTPException
from pydantic.schema import UUID

from src.api.request_models.request import Status
from src.bot.services import BotService
from src.core.db.repository.request_repository import (
    RequestRepository,
    request_repository,
)

REVIEWED_REQUEST = "Заявка была обработана, статус заявки: {}."


class RequestService:
    def __init__(self, request_repository: RequestRepository = request_repository) -> None:
        self.__request_repository = request_repository
        self.__telegram_bot = BotService()

    async def approve_request(self, request_id: UUID) -> None:
        """Заявка одобрена: обновление статуса, уведомление участника в телеграм."""
        request = await self.__request_repository.get(request_id)
        if request.status is Status.APPROVED:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=REVIEWED_REQUEST.format(request.status))
        request.status = Status.APPROVED
        await self.__request_repository.update(request_id, request)
        await self.__telegram_bot.notify_approved_request(request.user)
        return

    async def decline_request(self, request_id: UUID) -> None:
        """Заявка отклонена: обновление статуса, уведомление участника в телеграм."""
        request = await self.__request_repository.get(request_id)
        if request.status is Status.DECLINED:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=REVIEWED_REQUEST.format(request.status))
        request.status = Status.DECLINED
        await self.__request_repository.update(request_id, request)
        await self.__telegram_bot.notify_declined_request(request.user)
        return

    async def get_approved_shift_user_ids(self, shift_id: UUID) -> list[UUID]:
        """Получить id одобренных участников смены."""
        return await self.__request_repository.get_shift_user_ids(shift_id)
