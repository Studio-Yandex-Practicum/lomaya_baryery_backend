from uuid import UUID

from fastapi import Depends

from src.core.db.models import Member
from src.core.db.repository import MemberRepository, RequestRepository


class MemberService:
    def __init__(
        self,
        request_repository: RequestRepository = Depends(),
        member_repository: MemberRepository = Depends(),
    ) -> None:
        self.__request_repository = request_repository
        self.__member_repository = member_repository

    async def create_members(self, shift_id: UUID) -> None:
        approved_requests = await self.__request_repository.get_approved_requests_by_shift(shift_id)
        members = tuple(
            Member(
                user_id=request.user_id,
                shift_id=shift_id,
                numbers_lombaryers=0,
                status=Member.Status.ACTIVE.value,
            )
            for request in approved_requests
        )
        await self.__member_repository.create_all(members)
