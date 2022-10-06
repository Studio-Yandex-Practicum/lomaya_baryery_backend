import random
from typing import List, Tuple
from datetime import date, timedelta

from fastapi import Depends
from pydantic.schema import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Photo, UserTask
from src.core.services.request_sevice import RequestService
from src.core.services.task_service import get_task_service
from src.core.db.repository.request_repository import RequestRepository


class UserTaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_none(
        self,
        user_task_id: UUID,
    ) -> UserTask:
        """Получить объект отчета участника по id."""
        user_task = await self.session.execute(
            select(UserTask, Photo.url.label("photo_url")).where(UserTask.id == user_task_id)
        )
        return user_task.scalars().first()

    async def change_status(
        self,
        user_task: UserTask,
        status: UserTask.Status,
    ) -> UserTask:
        """Изменить статус задачи."""
        user_task.status = status
        self.session.add(user_task)
        await self.session.commit()
        await self.session.refresh(user_task)
        return user_task

    async def distribute_tasks_on_shift(
        self,
        shift_id: UUID,
    ) -> None:
        """Раздача участникам заданий на 3 месяца.

        Задачи раздаются случайным образом.
        Метод запускается при старте смены.
        """
        task_service = await get_task_service(self.session)
        request_service = RequestService(RequestRepository(self.session))
        task_ids_list = await task_service.get_task_ids_list()
        user_ids_list = await request_service.get_approved_shift_user_ids(shift_id)
        # Список 93 календарных дней, начиная с сегодняшнего
        dates_tuple = tuple((date.today() + timedelta(i)).day for i in range(93))

        def distribution_process(task_ids: List[UUID], dates: Tuple[int], user_id: UUID) -> None:
            """Процесс раздачи заданий пользователю."""
            # Для каждого пользователя
            # случайным образом перемешиваем список task_ids
            random.shuffle(task_ids)
            daynumbers_tuple = tuple(i for i in range(1, 94))
            # составляем кортеж из пар "день месяца - номер дня смены"
            date_to_daynumber_mapping = tuple(zip(dates, daynumbers_tuple))
            for date_day, day_number in date_to_daynumber_mapping:

                new_user_task = UserTask(
                    user_id=user_id,
                    shift_id=shift_id,
                    # Task_id на позиции, соответствующей дню месяца.
                    # Например, для первого числа это task_ids[0]
                    task_id=task_ids[date_day - 1],
                    day_number=day_number,
                )
                self.session.add(new_user_task)

        for userid in user_ids_list:
            distribution_process(task_ids_list, dates_tuple, userid)

        await self.session.commit()


def get_user_task_service(session: AsyncSession = Depends(get_session)) -> UserTaskService:
    return UserTaskService(session)
