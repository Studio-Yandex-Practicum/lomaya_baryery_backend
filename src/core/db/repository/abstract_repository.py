import abc
from typing import Optional, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

DatabaseModel = TypeVar("DatabaseModel")


class AbstractRepository(abc.ABC):
    """Абстрактный класс, для реализации паттерна Repository."""

    @abc.abstractmethod
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @abc.abstractmethod
    async def get_or_none(self, id: UUID) -> Optional[DatabaseModel]:
        """Получает из базы объект модели по ID. В случае отсутствия возвращает None."""
        pass

    @abc.abstractmethod
    async def get(self, id: UUID) -> DatabaseModel:
        """Получает объект модели по ID. В случае отсутствия объекта бросает ошибку."""
        pass

    @abc.abstractmethod
    async def create(self, instance: DatabaseModel) -> DatabaseModel:
        """Создает новый объект модели и сохраняет в базе."""
        pass

    @abc.abstractmethod
    async def update(self, id: UUID, instance: DatabaseModel) -> DatabaseModel:
        """Обновляет существующий объект модели в базе."""
        pass
