from abc import ABC

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.core.db.db import get_session


class HealthcheckRepository(ABC):
    """Репозиторий для обращения к бд сервисом HealthService."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def get_db_ver(self) -> str:
        query = text('SELECT VERSION()')
        db_ver = await self.session.execute(query)
        return db_ver.fetchone()
