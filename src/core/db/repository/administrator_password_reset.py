import datetime as dt

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Administrator, AdministratorPasswordReset
from src.core.db.repository import AbstractRepository


class AdministratorPasswordResetRepository(AbstractRepository):
    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, AdministratorPasswordReset)

    async def get_administrator_password_reset_by_email(self, email: str) -> AdministratorPasswordReset:
        """Возвращает объект восстановления пароля администратора."""
        administrator_password_reset = await self._session.execute(
            select(AdministratorPasswordReset).where(AdministratorPasswordReset.email == email)
        )
        return administrator_password_reset.scalars().one_or_none()

    async def administrator_password_reset_object_validation(self, token: str) -> bool:
        """Проверяет не привысило ли время жизни объекта AdministratorPasswordReset 10 минут."""
        administrator_password_reset = await self._session.execute(
            select(AdministratorPasswordReset).where(AdministratorPasswordReset.token == token)
        )
        update_time = administrator_password_reset.scalars().one_or_none()
        return (dt.datetime.utcnow() - update_time.updated_at).seconds < 600

    async def get_administrator_by_token(self, token: str) -> str:
        """Возвращает объект Administrator по токену для восстановления пароля."""
        administrator = await self._session.execute(
            (
                select(Administrator.id)
                .join(AdministratorPasswordReset, Administrator.email == AdministratorPasswordReset.email)
                .where(AdministratorPasswordReset.token == token)
            )
        )
        return administrator.one_or_none()
