from typing import Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Photo
from src.core.db.repository import AbstractRepository


class PhotoRepository(AbstractRepository):
    """Репозиторий для работы с моделью Photo."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        AbstractRepository.__init__(self, session, model=Photo)

    async def get_by_url(self, url: str) -> Optional[Photo]:
        photo = await self._session.execute(select(Photo).where(Photo.url == url))
        return photo.scalars().first()
