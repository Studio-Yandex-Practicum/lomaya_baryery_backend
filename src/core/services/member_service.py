from fastapi import Depends
from telegram.ext import Application

from src.bot import services
from src.core.db.models import Member
from src.core.db.repository.member_repository import MemberRepository


class MemberService:
    def __init__(self, member_repository: MemberRepository = Depends()) -> None:
        self.__member_repository = member_repository
        self.__telegram_bot = services.BotService

    async def exclude_members(self, members: list[Member], bot: Application.bot) -> None:
        """Исключает участников смены.

        Аргументы:
            members (list[Member]): список участников подлежащих исключению
        """
        await self.__member_repository.update_status_to_exclude(members)
        for member in members:
            await self.__telegram_bot(bot).notify_excluded_member(member.user)
