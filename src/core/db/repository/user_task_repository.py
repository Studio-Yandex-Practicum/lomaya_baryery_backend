from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import UserTask
from src.core.db.repository import AbstractRepository

STR_ENTITY_NOT_EXIST = "Задачи с указанным id не существует!"


class UserTaskRepository(AbstractRepository):
    """Репозиторий для работы с моделью Task."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def get_or_none(self, id: UUID) -> Optional[UserTask]:
        return await self.session.get(UserTask, id)

    async def get(self, id: UUID) -> UserTask:
        user_task = await self.get_or_none(id)
        if user_task is None:
            # # FIXME: написать и использовать кастомное исключение
            # raise LookupError(f"Объект UserTask c {id=} не найден.")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=STR_ENTITY_NOT_EXIST)
        return user_task

    async def create(self, user_task: UserTask) -> UserTask:
        self.session.add(user_task)
        await self.session.commit()
        await self.session.refresh(user_task)
        return user_task

    async def update(self, id: UUID, user_task: UserTask) -> UserTask:
        user_task.id = id
        await self.session.merge(user_task)
        await self.session.commit()
        return user_task

    async def update_status(self, id: UUID, status: UserTask.Status) -> UserTask:
        user_task = await self.get(id=id)
        user_task.status = status
        await self.session.merge(user_task)
        await self.session.commit()
        return user_task
