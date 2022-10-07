# import random
# from datetime import date, timedelta
# from typing import Any

from fastapi import Depends
from pydantic.schema import UUID

from src.api.request_models.user_task import ChangeStatusRequest

# from src.core.db.db import get_session
# from src.core.db.models import Task, User, UserTask
from src.core.db.models import UserTask
from src.core.db.repository.task_repository import TaskRepository
from src.core.db.repository.user_task_repository import UserTaskRepository

# from sqlalchemy import and_, or_, select
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from src.core.services.task_service import get_task_service


class UserTaskService:
    def __init__(
        self, user_task_repository: UserTaskRepository = Depends(), task_repository: TaskRepository = Depends()
    ) -> None:
        self.task_repository = task_repository
        self.user_task_repository = user_task_repository

    async def get_user_task(self, id: UUID) -> UserTask:
        return await self.user_task_repository.get(id)

    async def get_user_task_with_photo_url(self, id: UUID) -> dict:
        return await self.user_task_repository.get_user_task_with_photo_url(id)

    async def update_status(self, id: UUID, update_user_task_status: ChangeStatusRequest) -> dict:
        await self.user_task_repository.update(id=id, user_task=UserTask(**update_user_task_status.dict()))
        return await self.user_task_repository.get_user_task_with_photo_url(id)

    # async def distribute_tasks_on_shift(
    #         self,
    #         shift_id: UUID,
    # ) -> None:
    #     """Раздача участникам заданий на 3 месяца.
    #
    # Задачи раздаются случайным образом.
    # Метод запускается при старте смены.
    # """
    #
    # # task_service = await get_task_service(self.session)
    # # request_service = await get_request_service(self.session)
    # task_ids_list = await self.task_repository.get_task_ids_list()
    # user_ids_list = await request_service.get_user_ids_approved_to_shift(shift_id)
    # # Список 93 календарных дней, начиная с сегодняшнего
    # dates_tuple = tuple((date.today() + timedelta(i)).day for i in range(93))
    #
    # def distribution_process(task_ids: list[UUID], dates: tuple[int], user_id: UUID) -> None:
    #     """Процесс раздачи заданий пользователю."""
    #     # Для каждого пользователя
    #     # случайным образом перемешиваем список task_ids
    #     random.shuffle(task_ids)
    #     daynumbers_tuple = tuple(i for i in range(1, 94))
    #     # составляем кортеж из пар "день месяца - номер дня смены"
    #     date_to_daynumber_mapping = tuple(zip(dates, daynumbers_tuple))
    #     for date_day, day_number in date_to_daynumber_mapping:
    #         new_user_task = UserTask(
    #             user_id=user_id,
    #             shift_id=shift_id,
    #             # Task_id на позиции, соответствующей дню месяца.
    #             # Например, для первого числа это task_ids[0]
    #             task_id=task_ids[date_day - 1],
    #             day_number=day_number,
    #         )
    #         self.session.add(new_user_task)
    #
    # for userid in user_ids_list:
    #     distribution_process(task_ids_list, dates_tuple, userid)
    #
    # await self.session.commit()
