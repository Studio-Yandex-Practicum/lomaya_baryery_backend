from http import HTTPStatus

from fastapi import Depends, HTTPException
from pydantic.schema import UUID
from telegram.ext import Application

from src.api.request_models.request import Status
from src.bot import services
from src.core.db.repository import RequestRepository

REVIEWED_REQUEST = "Заявка была обработана, статус заявки: {}."


class RequestService:
    def __init__(self, request_repository: RequestRepository = Depends()) -> None:
        self.__request_repository = request_repository
        self.__telegram_bot = services.BotService()

    async def approve_request(self, request_id: UUID, bot: Application.bot) -> None:
        """Заявка одобрена: обновление статуса, уведомление участника в телеграм."""
        request = await self.__request_repository.get(request_id)
        if request.status is Status.APPROVED:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=REVIEWED_REQUEST.format(request.status))
        request.status = Status.APPROVED
        __telegram_bot = services.BotService(bot)
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
        __telegram_bot = services.BotService(bot)
        await __telegram_bot.notify_declined_request(request.user)
        return

    async def get_approved_shift_user_ids(self, shift_id: UUID) -> list[UUID]:
        """Получить id одобренных участников смены."""
        return await self.__request_repository.get_shift_user_ids(shift_id)

    async def exclude_members(self, user_ids: list[UUID], shift_id: UUID, bot: Application.bot) -> None:
        """Исключает участников смены.

        Аргументы:
            user_ids (list[UUID]): список id участников подлежащих исключению
            shift_id (UUID): id активной смены
        """
        requests = await self.__request_repository.get_requests_by_users_ids_and_shifts_id(user_ids, shift_id)
        if len(requests) == 0:
            raise LookupError(f'Заявки не найдены для участников с id {user_ids} в смене с id {shift_id}')
        await self.__request_repository.bulk_excluded_status_update(requests)
        __telegram_bot = services.BotService(bot)
        for request in requests:
            await __telegram_bot.notify_excluded_member(request.user)
