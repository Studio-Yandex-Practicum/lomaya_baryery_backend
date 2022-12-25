from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Administrator
from src.core.db.repository import AbstractRepository


class AdministratorRepository(AbstractRepository):
    """Репозиторий для работы с моделью Administrator."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Administrator)
