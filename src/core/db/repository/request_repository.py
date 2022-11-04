from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.db.db import get_session
from src.core.db.models import Request
from src.core.db.repository import AbstractRepository


class RequestRepository(AbstractRepository):
    """Репозиторий для работы с моделью Request."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def get_or_none(self, id: UUID) -> Optional[Request]:
        return await self.session.get(Request, id)

    async def get(self, id: UUID) -> Request:
        request = await self.session.execute(
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

    async def create(self, request: Request) -> Request:
        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def update(self, id: UUID, request: Request) -> Request:
        request.id = id
        await self.session.merge(request)
        await self.session.commit()
        return request

    async def get_shift_user_ids(self, shift_id: UUID, status: str = Request.Status.APPROVED.value) -> list[UUID]:
        users_ids = await self.session.execute(
            select(Request.user_id).where(Request.shift_id == shift_id).where(Request.status == status)
        )
        return users_ids.scalars().all()

    async def get_user_request_id_by_user_id_and_shift_id(self, user_id: UUID, shift_id: UUID) -> UUID:
        """Возвращает id заявки участника на смену по id участника и смены.

        Аргументы:
            user_id (UUID): id пользователя,
            shift_id (UUID): id смены, в которой участвует пользователь.
        """
        statement = (
            select(Request.id)
            .where(
                and_(
                    Request.user_id == user_id,
                    Request.shift_id == shift_id,
                    Request.deleted.is_(False),
                )
            )
            .options(
                selectinload(Request.user),
                selectinload(Request.shift),
            )
        )
        requests_ids = await self.session.scalars(statement)
        return requests_ids.first()
