from fastapi import Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import exceptions
from src.core.db.db import get_session
from src.core.db.models import Administrator
from src.core.db.repository import AbstractRepository


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
            raise exceptions.AdministratorNotFoundError
        return administrator

    async def is_administrator_exists(
        self,
        email: str,
        role: Administrator.Role | None = None,
    ) -> bool:
        """Проверяет существование администратора в БД.

        Args:
            email (str): email администратора.
            role (Administrator.Role): роль администратора; если None — то роль администратора не проверяется.

        Returns:
            bool: True — если администратор есть в БД, False — если нет
        """
        statement = select(Administrator).filter_by(email=email)

        if role is not None:
            statement = statement.filter_by(role=role)

        statement = select(statement.exists())

        return (await self._session.execute(statement)).scalar()

    async def get_administrators_filter_by_role_and_status(
        self, status: Administrator.Status | None, role: Administrator.Role | None
    ) -> list[Administrator]:
        """Возвращает из БД список администраторов отсортированный по фамилии и имени по возрастанию.

        Фильтрует результат в зависимости от переданных параметров

        Аргументы:
            status (Administrator.Status): требуемый статус администраторов
            role (Administrator.Role): требуемая роль администраторов
        """
        statement = (
            select(Administrator)
            .where(or_(status is None, Administrator.status == status), or_(role is None, Administrator.role == role))
            .order_by(Administrator.surname, Administrator.name)
        )
        return (await self._session.scalars(statement)).all()

    async def get_administrators_active(self) -> list[Administrator]:
        """Возвращает из БД список активных администраторов."""
        statement = select(Administrator).where(Administrator.status == "active")
        return (await self._session.scalars(statement)).all()
