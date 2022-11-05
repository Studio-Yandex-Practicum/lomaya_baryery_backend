from http import HTTPStatus
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.db.models import Request
from src.core.db.repository import AbstractRepository


class RequestRepository(AbstractRepository):
    """Репозиторий для работы с моделью Request."""

    async def get(self, id: UUID) -> Request:
        request = await self.__session.execute(
            select(Request)
            .where(Request.id == id)
            .options(
                selectinload(Request.user),
                selectinload(Request.shift),
            )
        )
        request = request.scalars().first()
        if request is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Объект Request c id={id} не найден.")
        return request

    async def get_by_user_and_shift(self, user_id: UUID, shift_id: UUID) -> Request:
        request = await self.session.execute(
            select(Request).where(Request.user_id == user_id, Request.shift_id == shift_id)
        )
        return request.scalars().first()

    async def add_one_lombaryer(self, request: Request) -> None:
        if not request.numbers_lombaryers:
            request.numbers_lombaryers = 1
        else:
            request.numbers_lombaryers += 1
        await self.session.merge(request)
        await self.session.commit()

    async def get_shift_user_ids(self, shift_id: UUID, status: str = Request.Status.APPROVED.value) -> list[UUID]:
        users_ids = await self.__session.execute(
            select(Request.user_id).where(Request.shift_id == shift_id).where(Request.status == status)
        )
        return users_ids.scalars().all()


request_repository = RequestRepository(Request)
