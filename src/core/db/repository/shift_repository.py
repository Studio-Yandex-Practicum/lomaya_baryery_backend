from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.response_models.shift import ShiftDtoRespone
from src.core.db.db import get_session
from src.core.db.models import Request, Shift, User
from src.core.db.repository import AbstractRepository


class ShiftRepository(AbstractRepository):
    """Репозиторий для работы с моделью Shift."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def get_or_none(self, id: UUID) -> Optional[Shift]:
        return await self.session.get(Shift, id)

    async def get(self, id: UUID) -> Shift:
        shift = await self.get_or_none(id)
        if shift is None:
            # FIXME: написать и использовать кастомное исключение
            raise LookupError(f"Объект Shift c {id=} не найден.")
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

    async def get_with_users(self, id: UUID, pagination) -> Shift:
        statement = select(Shift).where(Shift.id == id).options(selectinload(Shift.users))
        request = await paginate(self.session, statement, pagination)
        request = request.scalars().first()
        if request is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
        return await request

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
