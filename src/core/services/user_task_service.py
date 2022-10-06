# import random
# from datetime import date, timedelta
# from typing import Any

from fastapi import Depends
from pydantic.schema import UUID

from src.api.request_models.user_task import ChangeStatusRequest

# from src.core.db.db import get_session
# from src.core.db.models import Task, User, UserTask
from src.core.db.models import UserTask
from src.core.db.repository.user_task_repository import UserTaskRepository

# from sqlalchemy import and_, or_, select
# from sqlalchemy.ext.asyncio import AsyncSession

# from src.core.services.task_service import get_task_service


class UserTaskService:
    def __init__(self, user_task_repository: UserTaskRepository = Depends()) -> None:
        self.user_task_repository = user_task_repository

    async def get_user_task(self, id: UUID) -> UserTask:
        return await self.user_task_repository.get(id)

    async def get_user_task_with_photo_url(self, id: UUID) -> dict:
        return await self.user_task_repository.get_user_task_with_photo_url(id)

    async def update_status(self, id: UUID, update_user_task_status: ChangeStatusRequest) -> dict:
        await self.user_task_repository.update(id=id, user_task=UserTask(**update_user_task_status.dict()))
        return await self.user_task_repository.get_user_task_with_photo_url(id)


# class UserTaskService:
#     """Вспомогательный класс для UserTask.
#
#     Внутри реализованы методы для формирования итогового
#     отчета с информацией о смене и непроверенных задачах пользователей
#     с привязкой к смене и дню.
#
#     Метод 'get_tasks_report' формирует отчет с информацией о задачах
#     и юзерах.
#     Метод 'get' возвращает экземпляр UserTask по id.
#     """
#     #
#     # def __init__(self, session: AsyncSession):
#     #     self.session = session
#
#     async def _get_all_ids_callback(
#         self,
#         shift_id: UUID,
#         day_number: int,
#     ) -> list[tuple[int]]:
#         """Получает список кортежей с id всех UserTask, id всех юзеров и id задач этих юзеров."""
#         user_tasks_info = await self.session.execute(
#             select(UserTask.id, UserTask.user_id, UserTask.task_id)
#             .where(
#                 and_(
#                     UserTask.shift_id == shift_id,
#                     UserTask.day_number == day_number,
#                     or_(UserTask.status == UserTask.Status.NEW, UserTask.status == UserTask.Status.UNDER_REVIEW),
#                 )
#             )
#             .order_by(UserTask.id)
#         )
#         user_tasks_ids = user_tasks_info.all()
#         return user_tasks_ids
#
#     async def get_tasks_report(self, shift_id: UUID, day_number: int) -> list[dict[str, Any]]:
#         """Формирует итоговый список 'tasks' с информацией о задачах и юзерах."""
#         user_task_ids = await self._get_all_ids_callback(shift_id, day_number)
#         tasks = []
#         if not user_task_ids:
#             return tasks
#         for user_task_id, user_id, task_id in user_task_ids:
#             task_summary_info = await self.session.execute(
#                 select(
#                     User.name,
#                     User.surname,
#                     Task.id.label("task_id"),
#                     Task.description.label("task_description"),
#                     Task.url.label("task_url"),
#                 )
#                 .select_from(User, Task)
#                 .where(User.id == user_id, Task.id == task_id)
#             )
#             task_summary_info = task_summary_info.all()
#             task = dict(*task_summary_info)
#             task["id"] = user_task_id
#             tasks.append(task)
#         return tasks
#
#
#
#     async def distribute_tasks_on_shift(
#         self,
#         shift_id: UUID,
#     ) -> None:
#         """Раздача участникам заданий на 3 месяца.
#
#         Задачи раздаются случайным образом.
#         Метод запускается при старте смены.
#         """
#         task_service = await get_task_service(self.session)
#         request_service = await get_request_service(self.session)
#         task_ids_list = await task_service.get_task_ids_list()
#         user_ids_list = await request_service.get_user_ids_approved_to_shift(shift_id)
#         # Список 93 календарных дней, начиная с сегодняшнего
#         dates_tuple = tuple((date.today() + timedelta(i)).day for i in range(93))
#
#         def distribution_process(task_ids: list[UUID], dates: tuple[int], user_id: UUID) -> None:
#             """Процесс раздачи заданий пользователю."""
#             # Для каждого пользователя
#             # случайным образом перемешиваем список task_ids
#             random.shuffle(task_ids)
#             daynumbers_tuple = tuple(i for i in range(1, 94))
#             # составляем кортеж из пар "день месяца - номер дня смены"
#             date_to_daynumber_mapping = tuple(zip(dates, daynumbers_tuple))
#             for date_day, day_number in date_to_daynumber_mapping:
#
#                 new_user_task = UserTask(
#                     user_id=user_id,
#                     shift_id=shift_id,
#                     # Task_id на позиции, соответствующей дню месяца.
#                     # Например, для первого числа это task_ids[0]
#                     task_id=task_ids[date_day - 1],
#                     day_number=day_number,
#                 )
#                 self.session.add(new_user_task)
#
#         for userid in user_ids_list:
#             distribution_process(task_ids_list, dates_tuple, userid)
#
#         await self.session.commit()
#
#
# def get_user_task_service(session: AsyncSession = Depends(get_session)) -> UserTaskService:
#     return UserTaskService(session)
#
