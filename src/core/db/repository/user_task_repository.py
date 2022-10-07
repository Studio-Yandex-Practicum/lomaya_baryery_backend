# import random
from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

# from src.api.response_models.user_task import UserTaskResponse
from src.core.db.db import get_session
from src.core.db.models import Photo, Task, User, UserTask
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
        # user_task = UserTaskResponse(*user_task)
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

    async def _get_all_ids_callback(
        self,
        shift_id: UUID,
        day_number: int,
    ) -> list[Union[Row, Row]]:
        """Получает список кортежей с id всех UserTask, id всех юзеров и id задач этих юзеров."""
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

    async def get_tasks_report(self, shift_id: UUID, day_number: int) -> list[dict[str, Any]]:
        """Формирует итоговый список 'tasks' с информацией о задачах и юзерах."""
        user_task_ids = await self._get_all_ids_callback(shift_id, day_number)
        tasks = []
        if not user_task_ids:
            return tasks
        for user_task_id, user_id, task_id in user_task_ids:
            task_summary_info = await self.session.execute(
                select(
                    User.name,
                    User.surname,
                    Task.id.label("task_id"),
                    Task.description.label("task_description"),
                    Task.url.label("task_url"),
                )
                .select_from(User, Task)
                .where(User.id == user_id, Task.id == task_id)
            )
            task_summary_info = task_summary_info.all()
            task = dict(*task_summary_info)
            task["id"] = user_task_id
            tasks.append(task)
        return tasks

    # async def distribute_tasks_on_shift(
    #         self,
    #         shift_id: UUID,
    # ) -> None:
    #     """Раздача участникам заданий на 3 месяца.
    #
    #     Задачи раздаются случайным образом.
    #     Метод запускается при старте смены.
    #     """
    #     task_service = await get_task_service(self.session)
    #     request_service = await get_request_service(self.session)
    #     task_ids_list = await task_service.get_task_ids_list()
    #     user_ids_list = await request_service.get_user_ids_approved_to_shift(shift_id)
    #     # Список 93 календарных дней, начиная с сегодняшнего
    #     dates_tuple = tuple((date.today() + timedelta(i)).day for i in range(93))
    #
    #     def distribution_process(task_ids: list[UUID], dates: tuple[int], user_id: UUID) -> None:
    #         """Процесс раздачи заданий пользователю."""
    #         # Для каждого пользователя
    #         # случайным образом перемешиваем список task_ids
    #         random.shuffle(task_ids)
    #         daynumbers_tuple = tuple(i for i in range(1, 94))
    #         # составляем кортеж из пар "день месяца - номер дня смены"
    #         date_to_daynumber_mapping = tuple(zip(dates, daynumbers_tuple))
    #         for date_day, day_number in date_to_daynumber_mapping:
    #             new_user_task = UserTask(
    #                 user_id=user_id,
    #                 shift_id=shift_id,
    #                 # Task_id на позиции, соответствующей дню месяца.
    #                 # Например, для первого числа это task_ids[0]
    #                 task_id=task_ids[date_day - 1],
    #                 day_number=day_number,
    #             )
    #             self.session.add(new_user_task)
    #
    #     for userid in user_ids_list:
    #         distribution_process(task_ids_list, dates_tuple, userid)
    #
    #     await self.session.commit()
