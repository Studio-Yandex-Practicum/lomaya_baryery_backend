from typing import Optional, Union
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Request
from src.core.db.repository import AbstractRepository


class RequestRepository(AbstractRepository):
    """Репозиторий для работы с моделью Request."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def get_or_none(self, id: UUID) -> Optional[Request]:
        return await self.session.get(Request, id)

    async def get_by_attribute(self, attr_name: str, attr_value: Union[str, bool]) -> Optional[Request]:
        attr = getattr(Request, attr_name)
        user = await self.session.execute(select(Request).where(attr == attr_value))
        return user.scalars().first()

    async def get(self, id: UUID) -> Request:
        request = await self.get_or_none(id)
        if request is None:
            # FIXME: написать и использовать кастомное исключение
            raise LookupError(f"Объект Request c {id=} не найден.")
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
