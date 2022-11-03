import abc
from http import HTTPStatus
from http.client import HTTPException
from typing import Optional, TypeVar
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session

DatabaseModel = TypeVar("DatabaseModel")


class AbstractRepository(abc.ABC):
    """Абстрактный класс, для реализации паттерна Repository."""

    @abc.abstractmethod
    def __init__(self, model: DatabaseModel, session: AsyncSession = Depends(get_session)) -> None:
        self.__session = session
        self.model = model

    @abc.abstractmethod
    async def get_or_none(self, id: UUID) -> Optional[DatabaseModel]:
        """Получает из базы объект модели по ID. В случае отсутствия возвращает None."""
        db_obj = await self.__session.execute(select(self.model).where(self.model.id == id))
        return db_obj.scalars().first()

    @abc.abstractmethod
    async def get(self, id: UUID) -> DatabaseModel:
        """Получает объект модели по ID. В случае отсутствия объекта бросает ошибку."""
        db_obj = await self.get(id)
        if db_obj is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
        return db_obj

    @abc.abstractmethod
    async def create(self, instance: DatabaseModel) -> DatabaseModel:
        """Создает новый объект модели и сохраняет в базе."""
        self.__session.add(instance)
        await self.__session.commit()
        await self.__session.refresh(instance)
        return instance

    @abc.abstractmethod
    async def update(self, id: UUID, instance: DatabaseModel) -> DatabaseModel:
        """Обновляет существующий объект модели в базе."""
        instance.id = id
        await self.__session.merge(instance)
        await self.__session.commit()
        return instance
