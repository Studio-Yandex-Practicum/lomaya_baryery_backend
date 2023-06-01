from datetime import timedelta
from pathlib import Path
from typing import Optional

from fastapi import Depends
from pydantic.schema import UUID
from telegram.ext import Application

from src.api.request_models.request import RequestDeclineRequest
from src.api.response_models.request import RequestResponse
from src.bot import services
from src.core import exceptions
from src.core.db.DTO_models import RequestDTO
from src.core.db.models import Member, Request, Shift, User
from src.core.db.repository import MemberRepository, RequestRepository, UserRepository
from src.core.services.report_service import ReportService
from src.core.services.shift_service import ShiftService
from src.core.settings import settings
from src.core.utils import get_current_task_date


class RequestService:
    def __init__(
        self,
        request_repository: RequestRepository = Depends(),
        member_repository: MemberRepository = Depends(),
        user_repository: UserRepository = Depends(),
        shift_service: ShiftService = Depends(),
        report_service: ReportService = Depends(),
    ) -> None:
        self.__request_repository = request_repository
        self.__member_repository = member_repository
        self.__user_repository = user_repository
        self.__shift_service = shift_service
        self.__report_service = report_service
        self.__telegram_bot = services.BotService

    async def __create_user_dir(self, user: User, request: Request) -> None:
        shift_dir = await self.__shift_service.get_shift_dir(request.shift_id)
        path = Path(settings.USER_REPORTS_DIR / shift_dir / str(user.id))
        path.mkdir(parents=True, exist_ok=True)

    async def approve_request(self, request_id: UUID, bot: Application) -> RequestResponse:
        """Одобрение заявки: обновление статуса, уведомление участника в телеграм."""
        request = await self.__request_repository.get(request_id)
        self.__exception_if_request_is_processed(request.status)
        request.status = Request.Status.APPROVED
        await self.__request_repository.update(request_id, request)
        user = request.user
        await self.__create_user_dir(user, request)
        if user.status is not User.Status.VERIFIED:
            user.status = User.Status.VERIFIED
            await self.__user_repository.update(user.id, user)
        member = Member(user_id=request.user_id, shift_id=request.shift_id)
        member = await self.__member_repository.create(member)
        shift = await self.__shift_service.get_shift(request.shift_id)
        if shift.status is Shift.Status.STARTED:
            await self.__report_service.create_not_participated_reports(member.id, shift)

        first_task_date = shift.started_at
        if get_current_task_date() >= shift.started_at:
            first_task_date = get_current_task_date() + timedelta(days=1)

        await self.__telegram_bot(bot).notify_approved_request(request.user, first_task_date.strftime('%d.%m.%Y'))
        return RequestResponse.parse_from(request)

    async def decline_request(
        self, request_id: UUID, bot: Application, decline_request_data: Optional[RequestDeclineRequest]
    ) -> RequestResponse:
        """Отклонение заявки: обновление статуса, уведомление участника в телеграм."""
        request = await self.__request_repository.get(request_id)
        self.__exception_if_request_is_processed(request.status)
        request.status = Request.Status.DECLINED
        await self.__request_repository.update(request_id, request)
        user = request.user
        if user.status is User.Status.PENDING:
            user.status = User.Status.DECLINED
            await self.__user_repository.update(user.id, user)
        await self.__telegram_bot(bot).notify_declined_request(request.user, decline_request_data)
        return RequestResponse.parse_from(request)

    async def get_requests_list(self, status: Optional[Request.Status]) -> list[RequestDTO]:
        """Список заявок на участие."""
        return await self.__request_repository.get_requests_list(status)

    @staticmethod
    def __exception_if_request_is_processed(status: Request.Status) -> None:
        """Если заявка была обработана ранее, выбрасываем исключение."""
        if status not in (Request.Status.PENDING,):
            raise exceptions.RequestAlreadyReviewedError(status)
