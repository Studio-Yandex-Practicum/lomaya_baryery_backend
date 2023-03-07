from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import AdministratorPasswordReset
from src.core.db.repository import AbstractRepository


class AdministratorPasswordResetRepository(AbstractRepository):
    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, AdministratorPasswordReset)

    async def get_administrator_password_reset(self, email: str) -> AdministratorPasswordReset:
        """Проверяет есть ли запись о восстановлении пароля в БД."""
        administrator_password_reset = await self._session.execute(
            select(AdministratorPasswordReset).where(AdministratorPasswordReset.email == email)
        )
        return administrator_password_reset.scalars().first()
