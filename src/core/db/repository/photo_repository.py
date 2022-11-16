from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Photo
from src.core.db.repository import AbstractRepository


class PhotoRepository(AbstractRepository):
    """Репозиторий для работы с моделью Photo."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def get_or_none(self, id: UUID) -> Optional[Photo]:
        return await self.session.get(Photo, id)

    async def get(self, id: UUID) -> Photo:
        photo = await self.get_or_none(id)
        if photo is None:
            # FIXME: написать и использовать кастомное исключение
            raise LookupError(f"Объект Photo c {id=} не найден.")
        return photo

    async def get_by_url(self, url: str) -> Optional[Photo]:
        photo = await self.session.execute(select(Photo).where(Photo.url == url))
        return photo.scalars().first()

    async def create(self, photo: Photo) -> Photo:
        self.session.add(photo)
        await self.session.commit()
        await self.session.refresh(photo)
        return photo

    async def update(self, id: UUID, photo: Photo) -> Photo:
        photo.id = id
        await self.session.merge(photo)
        await self.session.commit()
        return photo
