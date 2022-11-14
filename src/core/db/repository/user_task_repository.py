from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, false, or_, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.response_models.task import LongTaskResponse
from src.core.db.db import get_session
from src.core.db import DTO_models
from src.core.db.models import Photo, Shift, Task, User, UserTask
from src.core.db.repository import AbstractRepository


class UserTaskRepository(AbstractRepository):
    """Репозиторий для работы с моделью UserTask."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.__session = session

    async def get_or_none(self, id: UUID) -> Optional[UserTask]:
        user_task = await self.__session.execute(
            select(UserTask)
            .where(UserTask.id == id)
            .options(
                selectinload(UserTask.user),
                selectinload(UserTask.photo),
            )
        )
        return user_task.scalars().first()

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
        user_task = await self.__session.execute(
            select(
                UserTask.user_id,
                UserTask.id,
                UserTask.task_id,
                UserTask.task_date,
                UserTask.status,
                Photo.url.label("photo_url"),
            )
            .join(Photo)
            .where(UserTask.id == id, Photo.id == UserTask.photo_id)
        )
        user_task = user_task.all()
        return dict(*user_task)

    async def get_all_ids(
        self,
        shift_id: UUID,
        task_date: date,
    ) -> list[tuple[int]]:
        """Получить список кортежей с id всех UserTask, id всех юзеров и id задач этих юзеров."""
        user_tasks_info = await self.__session.execute(
            select(UserTask.id, UserTask.user_id, UserTask.task_id)
            .where(
                and_(
                    UserTask.shift_id == shift_id,
                    UserTask.task_date == task_date,
                    or_(UserTask.status == UserTask.Status.NEW, UserTask.status == UserTask.Status.UNDER_REVIEW),
                )
            )
            .order_by(UserTask.id)
        )
        return user_tasks_info.all()

    async def get_all_tasks_id_under_review(self) -> Optional[list[UUID]]:
        """Получить список id непроверенных задач."""
        all_tasks_id_under_review = await self.__session.execute(
            select(UserTask.task_id).select_from(UserTask).where(UserTask.status == UserTask.Status.UNDER_REVIEW)
        )
        return all_tasks_id_under_review.all()

    async def get_tasks_by_usertask_ids(self, usertask_ids: list[UUID]) -> list[LongTaskResponse]:
        """Получить список заданий с подробностями на каждого участника по usertask_id."""
        tasks = await self.__session.execute(
            select(
                Task.id.label("task_id"),
                Task.url.label("task_url"),
                Task.description.label("task_description"),
                User.telegram_id.label("user_telegram_id"),
            )
            .where(UserTask.id.in_(usertask_ids))
            .join(UserTask.task)
            .join(UserTask.user)
        )
        tasks = tasks.all()
        task_infos = []
        for task in tasks:
            task_info = LongTaskResponse(**task)
            task_infos.append(task_info)
        return task_infos

    async def create(self, user_task: UserTask) -> UserTask:
        self.__session.add(user_task)
        await self.__session.commit()
        await self.__session.refresh(user_task)
        return user_task

    async def create_all(self, user_tasks_list: list[UserTask]) -> UserTask:
        self.__session.add_all(user_tasks_list)
        await self.__session.commit()
        return user_tasks_list

    async def update(self, id: UUID, user_task: UserTask) -> UserTask:
        user_task.id = id
        await self.__session.merge(user_task)
        await self.__session.commit()
        return user_task

    async def get_user_task_summary(
        self,
        shift_id: UUID,
        status: UserTask.Status
    ) -> list[DTO_models.FullUserTaskDto]:
        """Получить отчет участника по id с url фото выполненного задания."""
        stmt = select(Shift.id, Shift.status, Shift.started_at,
                      UserTask.id, UserTask.created_at,
                      User.name, User.surname,
                      UserTask.task_id,
                      Task.description, Task.url,
                      Photo.url
                      )
        if shift_id:
            stmt = stmt.where(UserTask.shift_id == shift_id)
        if status:
            stmt = stmt.where(UserTask.status == status)
        stmt = stmt.join(Shift).join(User).join(Task).join(Photo).order_by(desc(Shift.started_at))
        user_tasks = await self.__session.execute(stmt)
        return [DTO_models.FullUserTaskDto(*user_task) for user_task in user_tasks.all()]

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
