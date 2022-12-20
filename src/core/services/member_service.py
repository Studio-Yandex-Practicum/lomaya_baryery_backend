from fastapi import Depends
from telegram.ext import Application

from src.bot import services
from src.core.db.models import Member
from src.core.db.repository import MemberRepository, ShiftRepository
from src.core.settings import settings


class MemberService:
    def __init__(
        self,
        member_repository: MemberRepository = Depends(),
        shift_repository: ShiftRepository = Depends(),
    ) -> None:
        self.__member_repository = member_repository
        self.__shift_repository = shift_repository
        self.__telegram_bot = services.BotService

    async def exclude_lagging_members(self, bot: Application.bot) -> None:
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
            await self.__telegram_bot(bot).notify_excluded_member(member.user)
