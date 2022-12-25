from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import asc, case, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.request_models.user import UserDescAscSortRequest, UserFieldSortRequest
from src.api.response_models.user import UserWithStatusResponse
from src.core.db.db import get_session
from src.core.db.models import Member, Report, Shift, User
from src.core.db.repository import AbstractRepository


class UserRepository(AbstractRepository):
    """Репозиторий для работы с моделью User."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, User)

    async def get_user_by_id(self, user_id: UUID) -> User:
        """Получает объект пользователя по его id."""
        user = await self._session.execute(select(User).where(User.id == user_id))
        return user.scalars().first()

    async def get_user_by_id_with_shifts_detail(self, user_id: UUID) -> list:
        """
        Получает список смен, участником которых является пользователь.

        К каждой смене добавлены результаты агрегирующих функций,
        подсчитывающие количество задач пользователя в текущей смене
        по статусу.
        """
        stmt = (
            select(
                Shift.id,
                Shift.title,
                Shift.started_at,
                Shift.finished_at,
                Member.numbers_lombaryers,
                func.count(case([((Report.status == "approved"), Report.id)])).label('total_approved'),
                func.count(case([((Report.status == "declined"), Report.id)])).label('total_declined'),
                func.count(case([((Report.status == "reviewing"), Report.id)])).label('total_reviewing'),
            )
            .join(User.members, isouter=True)
            .join(Member.shift, isouter=True)
            .join(Member.reports, isouter=True)
            .group_by(Member.numbers_lombaryers, Shift.id)
            .where(User.id == user_id)
        )
        list_user_shifts = await self._session.execute(stmt)
        return list_user_shifts.all()

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
        status: Optional[User.Status] = None,
        field_sort: Optional[UserFieldSortRequest] = None,
        direction_sort: Optional[UserDescAscSortRequest] = None,
    ) -> list[UserWithStatusResponse]:
        sorting = {'desc': desc, 'asc': asc}
        users = await self._session.execute(
            select(
                User.id,
                User.name,
                User.surname,
                User.date_of_birth,
                User.city,
                User.phone_number,
                User.status,
            )
            .where(
                or_(status is None, User.status == status),
            )
            .order_by(sorting[direction_sort.value if direction_sort else 'asc'](field_sort or User.created_at))
        )
        return users.all()
