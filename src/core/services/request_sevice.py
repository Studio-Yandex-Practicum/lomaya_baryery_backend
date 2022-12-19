from http import HTTPStatus

from fastapi import Depends, HTTPException
from pydantic.schema import UUID
from telegram.ext import Application

from src.api.request_models.request import RequestDeclineRequest
from src.api.response_models.request import RequestResponse
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
        self,
        request_id: UUID,
        bot: Application,
        decline_request_data: RequestDeclineRequest | None,
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

    async def exclude_members(self, user_ids: list[UUID], shift_id: UUID, bot: Application) -> None:
        """Исключает участников смены.

        Аргументы:
            user_ids (list[UUID]): список id участников подлежащих исключению
            shift_id (UUID): id активной смены
        """
        requests = await self.__request_repository.get_requests_by_users_ids_and_shifts_id(user_ids, shift_id)
        if len(requests) == 0:
            raise LookupError(f'Заявки не найдены для участников с id {user_ids} в смене с id {shift_id}')
        await self.__request_repository.bulk_excluded_status_update(requests)
        for request in requests:
            await self.__telegram_bot(bot).notify_excluded_member(request.user)
