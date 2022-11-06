from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.response_models.shift import ShiftDtoRespone
from src.core.db.db import get_session
from src.core.db.models import Request, Shift, User, UserTask
from src.core.db.repository import AbstractRepository
from src.core.exceptions import NotFoundException


class ShiftRepository(AbstractRepository):
    """Репозиторий для работы с моделью Shift."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def get_or_none(self, id: UUID) -> Optional[Shift]:
        return await self.session.get(Shift, id)

    async def get(self, id: UUID) -> Shift:
        shift = await self.get_or_none(id)
        if shift is None:
            raise NotFoundException(object_name=Shift.__doc__, object_id=id)
        return shift

    async def create(self, shift: Shift) -> Shift:
        self.session.add(shift)
        await self.session.commit()
        await self.session.refresh(shift)
        return shift

    async def update(self, id: UUID, shift: Shift) -> Shift:
        shift.id = id
        shift = await self.session.merge(shift)
        await self.session.commit()
        return shift

    async def get_with_users(self, id: UUID) -> Shift:
        statement = select(Shift).where(Shift.id == id).options(selectinload(Shift.users))
        request = await self.session.execute(statement)
        request = request.scalars().first()
        if request is None:
            raise NotFoundException(object_name=Shift.__doc__, object_id=id)
        return request

    async def list_all_requests(self, id: UUID, status: Optional[Request.Status]) -> list[ShiftDtoRespone]:
        db_list_request = await self.session.execute(
            select(
                (Request.user_id),
                (Request.id.label("request_id")),
                (Request.status),
                (User.name),
                (User.surname),
                (User.date_of_birth),
                (User.city),
                (User.phone_number.label("phone")),
            )
            .join(Request.user)
            .where(
                or_(Request.shift_id == id),
                # Добавление условия запроса к бд если есть статус,
                # а если нету то получение всех записей из бд по shift_id
                or_(status is None, Request.status == status),
            )
        )
        return db_list_request.all()

    async def get_today_active_user_task_ids(self) -> list[UUID]:
        task_date = datetime.now().date()
        active_task_ids = await self.session.execute(
            select(UserTask.id)
            .where(UserTask.task_date == task_date, Request.status == Request.Status.APPROVED.value)
            .join(Shift.user_tasks)
            .join(Shift.requests)
        )
        return active_task_ids.scalars().all()
