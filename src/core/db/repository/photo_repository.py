from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Photo
from src.core.db.repository import AbstractRepository


class PhotoRepository(AbstractRepository):
    """Репозиторий для работы с моделью Photo."""

    _model = Photo

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self._session = session
