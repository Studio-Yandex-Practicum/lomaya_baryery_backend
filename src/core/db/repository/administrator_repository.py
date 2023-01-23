from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Administrator
from src.core.db.repository import AbstractRepository
from src.core.exceptions import AdministratorNotFoundException


class AdministratorRepository(AbstractRepository):
    """Репозиторий для работы с моделью Administrator."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Administrator)

    async def get_by_email(self, email: str) -> Administrator:
        """Получает из БД администратора по его email. В случае отсутствия бросает ошибку.

        Аргументы:
            email (str) - email администратора.
        """
        administrator = await self._session.execute(select(Administrator).where(Administrator.email == email))
        administrator = administrator.scalars().first()
        if not administrator:
            raise AdministratorNotFoundException()
        return administrator
