from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.response_models.shift import ShiftUsersResponse
from src.core.db.db import get_session
from src.core.db.models import Request, User
from src.core.db.repository.shift_repository import ShiftRepository


class UserService:
    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
        shift_repository: ShiftRepository = Depends(),
    ) -> None:
        self.shift_repository = shift_repository
        self.session = session

    async def get_user_list_by_shift_id(self, shift_id: UUID) -> ShiftUsersResponse:
        """Получаем смену и список пользователей зарегистрированных на смену по shift_id."""
        shift = await self.shift_repository.get(shift_id)
        statement = select(User).where(and_(Request.user_id == User.id, Request.shift_id == shift_id))
        users = await self.session.execute(statement)
        users = users.scalars().all()
        return ShiftUsersResponse(shift=shift, users=users)
