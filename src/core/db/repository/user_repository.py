from typing import Optional

from fastapi import Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.request_models.user import UserSortRequest
from src.core.db.db import get_session
from src.core.db.models import Request, User
from src.core.db.repository import AbstractRepository


class UserRepository(AbstractRepository):
    """Репозиторий для работы с моделью User."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, User)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        user = await self._session.execute(select(User).where(User.telegram_id == telegram_id))
        return user.scalars().first()

    async def check_user_existence(self, telegram_id: int, phone_number: str) -> bool:
        user_exists = await self._session.execute(
            select(select(User).where(or_(User.phone_number == phone_number, User.telegram_id == telegram_id)).exists())
        )
        return user_exists.scalar()

    async def get_users_with_status(
        self,
        status: Optional[Request.Status],
        sort: Optional[UserSortRequest],
    ) -> list:
        users = (
            select(
                User.id,
                User.name,
                User.surname,
                User.date_of_birth,
                User.city,
                User.phone_number,
                Request.status.label('status'),
            )
            .join(User.requests)
            .where(
                or_(status is None, Request.status == status),
            )
            .order_by(sort or User.id.desc())
        )
        users = await self._session.execute(users)
        return users.all()
