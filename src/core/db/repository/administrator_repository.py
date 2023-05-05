from fastapi import Depends
from sqlalchemy import and_, or_, select
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

    async def administrator_exists(self, email: str) -> bool:
        """Проверяет существование администратора по email.

        Args:
            email (str) - email администратора.

        Returns:
            bool: True — если администратор есть в БД, False — если нет
        """
        administrator_exists = await self._session.execute(
            select(select(Administrator).where(Administrator.email == email).exists())
        )
        return administrator_exists.scalar()

    async def administrator_is_active(self, email: str) -> bool:
        """Проверяет существование активного администратора с ролью admin по email.

        Args:
            email (str) - email администратора.

        Returns:
            bool: True — если администратор есть в БД, False — если нет
        """
        stmt = select(
            select(Administrator)
            .where(and_(Administrator.email == email, Administrator.status == Administrator.Status.ACTIVE))
            .exists()
        )
        administrator_exists = await self._session.execute(stmt)
        return administrator_exists.scalar()

    async def administrator_is_active_and_is_admin(self, email: str) -> bool:
        """Проверяет существование активного администратора с ролью admin по email.

        Args:
            email (str) - email администратора.

        Returns:
            bool: True — если администратор есть в БД, False — если нет
        """
        stmt = select(
            select(Administrator)
            .where(
                and_(
                    Administrator.email == email,
                    Administrator.status == Administrator.Status.ACTIVE,
                    Administrator.role == Administrator.Role.ADMINISTRATOR,
                )
            )
            .exists()
        )
        administrator_exists = await self._session.execute(stmt)
        return administrator_exists.scalar()

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
