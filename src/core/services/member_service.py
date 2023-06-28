from uuid import UUID

from fastapi import Depends
from telegram.ext import Application

from src.bot import services
from src.core.db.models import Member, Shift
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

    async def exclude_lagging_members(self, shift: Shift, bot: Application) -> None:
        """Исключает участников из стартовавшей смены.

        Если участники не посылают отчет о выполненом задании указанное
        в настройках количество раз подряд, то они будут исключены из смены.
        """
        lagging_members = await self.__member_repository.get_members_for_excluding(
            shift.id, settings.SEQUENTIAL_TASKS_PASSES_FOR_EXCLUDE
        )
        for member in lagging_members:
            member.status = Member.Status.EXCLUDED
            await self.__member_repository.update(member.id, member)
        await self.__telegram_bot(bot).notify_excluded_members(lagging_members)

    async def get_members_with_no_reports(self, shift_id: UUID) -> list[Member]:
        """Получить всех участников, у которых отчеты в статусе WAITING."""
        current_task_date = get_current_task_date()
        return await self.__member_repository.get_members_for_reminding(shift_id, current_task_date)

    async def get_number_of_lombariers_by_telegram_id(self, telegram_id) -> int:
        """Получение баланса ломбарьеров в текущей смене по telegram_id."""
        return await self.__member_repository.get_number_of_lombariers_by_telegram_id(telegram_id)
