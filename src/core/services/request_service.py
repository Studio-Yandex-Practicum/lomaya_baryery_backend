from http import HTTPStatus
from typing import Optional

from fastapi import Depends, HTTPException
from pydantic.schema import UUID
from telegram.ext import Application

from src.api.request_models.request import RequestDeclineRequest, Status
from src.api.response_models.request import (
    RequestResponse,
    RequestWithUserStatusResponse,
)
from src.bot import services
from src.core.db.models import Member, Request
from src.core.db.repository import MemberRepository, RequestRepository
from src.core.exceptions import SendTelegramNotifyException

REVIEWED_REQUEST = "Заявка была обработана, статус заявки: {}."


class RequestService:
    def __init__(
        self,
        request_repository: RequestRepository = Depends(),
        member_repository: MemberRepository = Depends(),
    ) -> None:
        self.__request_repository = request_repository
        self.__member_repository = member_repository
        self.__telegram_bot = services.BotService

    async def approve_request(self, request_id: UUID, bot: Application) -> RequestResponse:
        """Заявка одобрена: обновление статуса, уведомление участника в телеграм."""
        request = await self.__request_repository.get(request_id)
        if request.status not in (Request.Status.PENDING, Request.Status.REPEATED_REQUEST):
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=REVIEWED_REQUEST.format(request.status))
        try:
            await self.__telegram_bot(bot).notify_approved_request(request.user)
        except Exception as exc:
            raise SendTelegramNotifyException(
                request.user.id, request.user.name, request.user.surname, request.user.telegram_id, exc
            )
        request.status = Request.Status.APPROVED
        await self.__request_repository.update(request_id, request)
        member = Member(user_id=request.user_id, shift_id=request.shift_id)
        await self.__member_repository.create(member)
        return RequestResponse.parse_from(request)

    async def decline_request(
        self, request_id: UUID, bot: Application, decline_request_data: Optional[RequestDeclineRequest]
    ) -> RequestResponse:
        """Заявка отклонена: обновление статуса, уведомление участника в телеграм."""
        request = await self.__request_repository.get(request_id)
        if request.status not in (Request.Status.PENDING, Request.Status.REPEATED_REQUEST):
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=REVIEWED_REQUEST.format(request.status))
        try:
            await self.__telegram_bot(bot).notify_declined_request(request.user, decline_request_data)
        except Exception as exc:
            raise SendTelegramNotifyException(
                request.user.id, request.user.name, request.user.surname, request.user.telegram_id, exc
            )
        request.status = Request.Status.DECLINED
        await self.__request_repository.update(request_id, request)
        return RequestResponse.parse_from(request)

    async def get_requests_list(self, status: Optional[Status]) -> list[RequestWithUserStatusResponse]:
        return await self.__request_repository.get_requests_list(status)
