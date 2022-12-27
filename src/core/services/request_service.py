from typing import Optional

from fastapi import Depends
from pydantic.schema import UUID
from telegram.ext import Application

from src.api.request_models.request import RequestDeclineRequest
from src.api.response_models.request import RequestResponse
from src.bot import services
from src.core.db.models import Member, Request, User
from src.core.db.repository import MemberRepository, RequestRepository, UserRepository
from src.core.exceptions import (
    RquestAcceptedException,
    RquestDeclinedException,
    SendTelegramNotifyException,
)


class RequestService:
    def __init__(
        self,
        request_repository: RequestRepository = Depends(),
        member_repository: MemberRepository = Depends(),
        user_repository: UserRepository = Depends(),
    ) -> None:
        self.__request_repository = request_repository
        self.__member_repository = member_repository
        self.__user_repository = user_repository
        self.__telegram_bot = services.BotService

    async def approve_request(self, request_id: UUID, bot: Application) -> RequestResponse:
        """Одобрение заявки: обновление статуса, уведомление участника в телеграм."""
        request = await self.__request_repository.get(request_id)
        request.status = Request.Status.APPROVED
        await self.__request_repository.update(request_id, request)
        user = self.__user_repository.get(request.user_id)
        user.status = User.Status.VERIFIED
        await self.__user_repository.update(user.id, user)
        member = Member(user_id=request.user_id, shift_id=request.shift_id)
        await self.__member_repository.create(member)
        if request.status is Request.Status.APPROVED:
            raise RquestAcceptedException
        try:
            await self.__telegram_bot(bot).notify_approved_request(request.user)
        except Exception as exc:
            raise SendTelegramNotifyException(
                request.user.id, request.user.name, request.user.surname, request.user.telegram_id, exc
            )
        return RequestResponse.parse_from(request)

    async def decline_request(
        self, request_id: UUID, bot: Application, decline_request_data: Optional[RequestDeclineRequest]
    ) -> RequestResponse:
        """Отклонение заявки: обновление статуса, уведомление участника в телеграм."""
        request = await self.__request_repository.get(request_id)
        request.status = Request.Status.DECLINED
        await self.__request_repository.update(request_id, request)
        user = self.__user_repository.get(request.user_id)
        user.status = User.Status.DECLINED
        await self.__user_repository.update(user.id, user)
        if request.status is Request.Status.DECLINED:
            raise RquestDeclinedException
        try:
            await self.__telegram_bot(bot).notify_declined_request(request.user, decline_request_data)
        except Exception as exc:
            raise SendTelegramNotifyException(
                request.user.id, request.user.name, request.user.surname, request.user.telegram_id, exc
            )
        return RequestResponse.parse_from(request)
