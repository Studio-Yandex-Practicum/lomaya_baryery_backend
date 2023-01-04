from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.db.db import get_session
from src.core.db.DTO_models import RequestDTO
from src.core.db.models import Request, User
from src.core.db.repository import AbstractRepository


class RequestRepository(AbstractRepository):
    """Репозиторий для работы с моделью Request."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Request)

    async def get(self, id: UUID) -> Request:
        request = await self._session.execute(
            select(Request)
            .where(Request.id == id)
            .options(
                selectinload(Request.user),
                selectinload(Request.shift),
            )
        )
        request = request.scalars().first()
        if request is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Объект Request c id={id} не найден.",
            )
        return request

    async def get_by_user_and_shift(self, user_id: UUID, shift_id: UUID) -> Request:
        request = await self._session.execute(
            select(Request).where(Request.user_id == user_id, Request.shift_id == shift_id)
        )
        return request.scalars().first()

    async def get_shift_user_ids(self, shift_id: UUID, status: str = Request.Status.APPROVED.value) -> list[UUID]:
        users_ids = await self._session.execute(
            select(Request.user_id).where(Request.shift_id == shift_id).where(Request.status == status)
        )
        return users_ids.scalars().all()

    async def get_approved_requests_by_shift(self, shift_id: UUID) -> list[Request]:
        approved_requests = await self._session.execute(
            select(Request).where(Request.shift_id == shift_id, Request.status == Request.Status.APPROVED.value)
        )
        return approved_requests.scalars().all()

    async def get_requests_list(self, status: Optional[Request.Status]) -> list[RequestDTO]:
        statement = select(
            Request.user_id,
            User.name,
            User.surname,
            User.date_of_birth,
            User.city,
            User.phone_number,
            User.status.label("user_status"),
            Request.id.label("request_id"),
            Request.status.label("request_status"),
        ).where(
            or_(status is None, Request.status == status),
            Request.user_id == User.id,
        )
        requests = await self._session.execute(statement)
        return [RequestDTO(**request) for request in requests.all()]
