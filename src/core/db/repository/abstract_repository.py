import abc
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel as PydanticModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import Base as DatabaseModel


class AbstractRepository(abc.ABC):
    """Абстрактный класс, реализующий паттерн Repository."""

    @abc.abstractmethod
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = DatabaseModel

    @abc.abstractmethod
    async def get(self, obj_id: UUID) -> DatabaseModel:
        return await self.session.scalar(select(self.model).where(self.model.id == obj_id))

    @abc.abstractmethod
    async def create(self, obj_data: PydanticModel) -> DatabaseModel:
        obj_data = obj_data.dict()
        db_obj = self.model(**obj_data)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    @abc.abstractmethod
    async def update(self, db_obj: DatabaseModel, obj_update_data: PydanticModel) -> DatabaseModel:
        obj_current_data = jsonable_encoder(db_obj)
        obj_update_data = obj_update_data.dict(exclude_unset=True)
        for field in obj_current_data:
            for field in obj_update_data:
                setattr(db_obj, field, obj_update_data[field])
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
