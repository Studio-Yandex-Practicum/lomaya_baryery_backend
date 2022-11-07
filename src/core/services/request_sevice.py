from http import HTTPStatus

from fastapi import Depends, HTTPException
from pydantic.schema import UUID
from telegram.ext import Application

from src.api.request_models.request import Status
from src.bot.services import BotService
from src.core.db.models import Request
from src.core.db.repository import RequestRepository

REVIEWED_REQUEST = "Заявка была обработана, статус заявки: {}."


class RequestService:
    def __init__(self, request_repository: RequestRepository = Depends()) -> None:
        self.__request_repository = request_repository

    async def approve_request(self, request_id: UUID, bot: Application.bot) -> None:
        """Заявка одобрена: обновление статуса, уведомление участника в телеграм."""
        request = await self.__request_repository.get(request_id)
        if request.status is Status.APPROVED:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=REVIEWED_REQUEST.format(request.status))
        request.status = Status.APPROVED
        __telegram_bot = BotService(bot)
        await self.__request_repository.update(request_id, request)
        await __telegram_bot.notify_approved_request(request.user)
        return

    async def decline_request(self, request_id: UUID, bot: Application.bot) -> None:
        """Заявка отклонена: обновление статуса, уведомление участника в телеграм."""
        request = await self.__request_repository.get(request_id)
        if request.status is Status.DECLINED:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=REVIEWED_REQUEST.format(request.status))
        request.status = Status.DECLINED
        await self.__request_repository.update(request_id, request)
        __telegram_bot = BotService(bot)
        await __telegram_bot.notify_declined_request(request.user)
        return

    async def exclude_user(self, user_id: UUID, shift_id: UUID, bot: Application.bot) -> None:
        """Исключает участника из смены, высылает уведомление в телеграм."""
        request = await self.get_request_with_user_and_shift_by_user_id_and_shift_id(user_id, shift_id)
        if request.status is Request.Status.EXCLUDED:
            raise HTTPException(HTTPStatus.NOT_FOUND, REVIEWED_REQUEST.format(request.status))
        request.status = Request.Status.EXCLUDED
        await self.__request_repository.update(request.id, request)
        __telegram_bot = BotService(bot)
        await __telegram_bot.notify_excluded_request(request.user)

    async def get_approved_shift_user_ids(self, shift_id: UUID) -> list[UUID]:
        """Получить id одобренных участников смены."""
        return await self.__request_repository.get_shift_user_ids(shift_id)

    async def get_request_with_user_and_shift_by_user_id_and_shift_id(self, user_id: UUID, shift_id: UUID) -> Request:
        """Возвращает заявку участника по id участника и смены вместе со связанными сущностями user и shift."""
        return await self.__request_repository.get_request_with_user_and_shift_by_user_id_and_shift_id(
            user_id, shift_id
        )
