from uuid import UUID

from fastapi import Depends
from telegram.ext import Application

from src.bot import services
from src.core.db.models import Member
from src.core.db.repository import MemberRepository, ShiftRepository
from src.core.settings import settings
from src.core.utils import get_current_task_date


class MemberService:
    def __init__(
        self,
        member_repository: MemberRepository = Depends(),
        shift_repository: ShiftRepository = Depends(),
    ) -> None:
        self.__member_repository = member_repository
        self.__shift_repository = shift_repository
        self.__telegram_bot = services.BotService

    async def exclude_lagging_members(self, bot: Application) -> None:
        """Исключает участников из стартовавшей смены.

        Если участники не посылают отчет о выполненом задании указанное
        в настройках количество раз подряд, то они будут исключены из смены.
        """
        shift_id = await self.__shift_repository.get_started_shift_id()
        lagging_members = await self.__member_repository.get_members_for_excluding(
            shift_id, settings.SEQUENTIAL_TASKS_PASSES_FOR_EXCLUDE
        )
        for member in lagging_members:
            member.status = Member.Status.EXCLUDED
            await self.__member_repository.update(member.id, member)
        await self.__telegram_bot(bot).notify_excluded_members(lagging_members)

    async def get_members_with_no_reports(self) -> list[Member]:
        """Получить всех участников, у которых отчеты в статусе WAITING."""
        shift_id = await self.__shift_repository.get_started_shift_id()
        current_task_date = get_current_task_date()
        return await self.__member_repository.get_members_for_reminding(shift_id, current_task_date)

    async def get_by_user_id_and_shift_id(self, shift_id: UUID, user_id: UUID) -> Member:
        """Получение участника по user_id и shift_id."""
        return await self.__member_repository.get_by_user_and_shift(shift_id, user_id)
