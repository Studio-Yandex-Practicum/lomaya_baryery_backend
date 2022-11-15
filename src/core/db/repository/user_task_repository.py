from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, case, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.response_models.task import LongTaskResponse
from src.core.db import DTO_models
from src.core.db.db import get_session
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

    async def get_summaries_of_user_tasks(
        self, shift_id: UUID, status: UserTask.Status
    ) -> list[DTO_models.FullUserTaskDto]:
        """Получить отчеты участников по id смены с url фото выполненного задания."""
        stmt = select(
            Shift.id,
            Shift.status,
            Shift.started_at,
            UserTask.id,
            UserTask.created_at,
            User.name,
            User.surname,
            UserTask.task_id,
            Task.description,
            Task.url,
            Photo.url,
        )
        if shift_id:
            stmt = stmt.where(UserTask.shift_id == shift_id)
        if status:
            stmt = stmt.where(UserTask.status == status)
        stmt = stmt.join(Shift).join(User).join(Task).join(Photo).order_by(desc(Shift.started_at))
        user_tasks = await self.__session.execute(stmt)
        return [DTO_models.FullUserTaskDto(*user_task) for user_task in user_tasks.all()]

    async def get_members_ids_for_excluding(self, shift_id: UUID, task_amount: int) -> list[UUID]:
        """Возвращает список id участников, кто не отправлял отчеты на задания указанное количество раз.

        Аргументы:
            shift_id (UUID): id стартовавшей смены
            task_amount (int): количество пропущенных заданий подряд, при котором участник считается неактивным.
        """
        subquery_rank = (
            select(
                func.rank().over(order_by=UserTask.task_date.desc(), partition_by=UserTask.user_id).label('rnk'),
                UserTask.user_id,
                UserTask.status,
            )
            .where(
                and_(
                    UserTask.shift_id == shift_id,
                    UserTask.status != UserTask.Status.NEW,
                    UserTask.deleted.is_(False),
                )
            )
            .subquery()
        )
        subquery_last_statuses = select(subquery_rank).where(subquery_rank.c.rnk <= task_amount).subquery()
        case_statement = case(
            (subquery_last_statuses.c.status == UserTask.Status.WAIT_REPORT, 1),
        )
        statement = (
            select(subquery_last_statuses.c.user_id)
            .having(func.count(case_statement) >= task_amount)
            .group_by(subquery_last_statuses.c.user_id)
        )
        return (await self.__session.scalars(statement)).all()

    async def set_usertasks_deleted(self, user_ids: list[UUID], shift_id: UUID) -> None:
        """Переводит задания участников указанных в user_ids в смене с id shift_id в статус удаленных.

        Аргументы:
            user_ids (list[UUID]): список id участников
            shift_id (UUID): id смены
        """
        statement = (
            update(UserTask)
            .where(
                and_(
                    UserTask.user_id.in_(user_ids),
                    UserTask.shift_id == shift_id,
                )
            )
            .values(deleted=True)
        )
        await self.__session.execute(statement)
        await self.__session.commit()
