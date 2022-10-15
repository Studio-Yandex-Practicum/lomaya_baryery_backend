from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, false, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Photo, UserTask
from src.core.db.repository import AbstractRepository


class UserTaskRepository(AbstractRepository):
    """Репозиторий для работы с моделью UserTask."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def get_or_none(self, id: UUID) -> Optional[UserTask]:
        return await self.session.get(UserTask, id)

    async def get(self, id: UUID) -> UserTask:
        user_task = await self.get_or_none(id)
        if user_task is None:
            # FIXME: написать и использовать кастомное исключение
            raise LookupError(f"Объект UserTask c {id=} не найден.")
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

    async def get_new_undeleted_by_user_id(self, user_id: UUID) -> Optional[UserTask]:
        """Получить наиболее раннюю задачу со статусом new и без признака удаления."""
        statement = (
            select(UserTask)
            .where(
                and_(UserTask.deleted == false(), UserTask.status == UserTask.Status.NEW, UserTask.user_id == user_id)
            )
            .order_by(UserTask.day_number)
        )
        user_tasks = await self.session.execute(statement)
        return user_tasks.scalars().first()
