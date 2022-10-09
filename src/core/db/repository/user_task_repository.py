from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Photo, UserTask
from src.core.db.repository.abstract_repository import AbstractRepository

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
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=STR_ENTITY_NOT_EXIST)
        return user_task

    async def get_user_task_with_photo_url(
        self,
        id: UUID,
    ) -> dict:
        """Получить отчет участника по id с url фото выполненного задания."""
        user_task = await self.session.execute(
            select(
                UserTask.user_id,
                UserTask.id,
                UserTask.task_id,
                UserTask.day_number,
                UserTask.status,
                Photo.url.label("photo_url"),
            )
            .join(Photo)
            .where(UserTask.id == id, Photo.id == UserTask.photo_id)
        )

        user_task = user_task.all()
        user_task = dict(*user_task)
        return user_task

    async def get_all_ids(
        self,
        shift_id: UUID,
        day_number: int,
    ) -> list[tuple[int]]:
        """Получить список кортежей с id всех UserTask, id всех юзеров и id задач этих юзеров."""
        user_tasks_info = await self.session.execute(
            select(UserTask.id, UserTask.user_id, UserTask.task_id)
            .where(
                and_(
                    UserTask.shift_id == shift_id,
                    UserTask.day_number == day_number,
                    or_(UserTask.status == UserTask.Status.NEW, UserTask.status == UserTask.Status.UNDER_REVIEW),
                )
            )
            .order_by(UserTask.id)
        )
        user_tasks_ids = user_tasks_info.all()
        return user_tasks_ids

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
