from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.request_models.request import GetListAllShiftRequests
from src.api.response_models.request import RequestDBRespone
from src.core.db.db import get_session
from src.core.db.models import Request, User
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
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Объект Request c id={id} не найден.")
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

    async def get_shift_user_ids(
            self, shift_id: UUID,
            status: str = Request.Status.APPROVED.value
    ) -> list[UUID]:
        users_ids = await self.session.execute(
            select(
                Request.user_id
            ).where(
                Request.shift_id == shift_id
            ).where(
                Request.status == status
            )
        )
        return users_ids.scalars().all()

    async def list_all_requests(
        self,
        request_status_and_shift_id: GetListAllShiftRequests,
    ) -> list[RequestDBRespone]:
        db_list_request = await self.session.execute(
            select((Request.user_id),
                   (Request.id.label("request_id")),
                   (Request.status),
                   (User.name),
                   (User.surname),
                   (User.date_of_birth),
                   (User.city),
                   (User.phone_number.label("phone")))
                   .join(Request.user)
                    .where(
                        or_(Request.shift_id == request_status_and_shift_id.shift_id),
                        #Добавление условия запроса к бд если есть статус,
                        # а если нету то получение всех записей из бд по shift_id
                        or_(request_status_and_shift_id.status is None,
                            Request.status == request_status_and_shift_id.status)
                        )
                    )
        return db_list_request.all()
