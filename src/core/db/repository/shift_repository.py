from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from src.api.response_models.shift import ShiftDtoRespone
from src.core.db.models import Request, Shift, User
from src.core.db.repository import AbstractRepository


class ShiftRepository(AbstractRepository):
    """Репозиторий для работы с моделью Shift."""

    async def get_with_users(self, id: UUID) -> Shift:
        statement = select(Shift).where(Shift.id == id).options(selectinload(Shift.users))
        request = await self.__session.execute(statement)
        request = request.scalars().first()
        if request is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
        return request

    async def list_all_requests(self, id: UUID, status: Optional[Request.Status]) -> list[ShiftDtoRespone]:
        db_list_request = await self.__session.execute(
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


shift_repository = ShiftRepository(Shift)
