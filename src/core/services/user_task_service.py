import random
from datetime import timedelta
from typing import Any

from fastapi import Depends
from pydantic.schema import UUID

from src.api.request_models.user_task import ChangeStatusRequest
from src.core.db.models import UserTask
from src.core.db.repository import RequestRepository, ShiftRepository, TaskRepository, UserTaskRepository
from src.core.services.request_sevice import RequestService
from src.core.services.task_service import TaskService


class UserTaskService:
    """Вспомогательный класс для UserTask.

    Внутри реализованы методы для формирования итогового
    отчета с информацией о смене и непроверенных задачах пользователей
    с привязкой к смене и дню.

    Метод 'get_tasks_report' формирует отчет с информацией о задачах
    и юзерах.
    Метод 'get' возвращает экземпляр UserTask по id.
    """

    def __init__(
        self,
        user_task_repository: UserTaskRepository = Depends(),
        task_repository: TaskRepository = Depends(),
        request_repository: RequestRepository = Depends(),
        shift_repository: ShiftRepository = Depends(),
        task_service: TaskService = Depends(),
        request_service: RequestService = Depends(),
    ) -> None:
        self.user_task_repository = user_task_repository
        self.task_repository = task_repository
        self.request_repository = request_repository
        self.shift_repository = shift_repository
        self.task_service = task_service
        self.request_service = request_service

    async def get_user_task(self, id: UUID) -> UserTask:
        return await self.user_task_repository.get(id)

    async def get_user_task_with_photo_url(self, id: UUID) -> dict:
        return await self.user_task_repository.get_user_task_with_photo_url(id)

    # TODO переписать
    async def get_tasks_report(self, shift_id: UUID, day_number: int) -> list[dict[str, Any]]:
        """Формирует итоговый список 'tasks' с информацией о задачах и юзерах."""
        user_task_ids = await self.user_task_repository.get_all_ids(shift_id, day_number)
        tasks = []
        if not user_task_ids:
            return tasks
        for user_task_id, user_id, task_id in user_task_ids:
            task = await self.task_repository.get_tasks_report(user_id, task_id)
            task["id"] = user_task_id
            tasks.append(task)
        return tasks

    async def update_status(self, id: UUID, update_user_task_status: ChangeStatusRequest) -> dict:
        await self.user_task_repository.update(id=id, user_task=UserTask(**update_user_task_status.dict()))
        return await self.user_task_repository.get_user_task_with_photo_url(id)

    # TODO переписать
    async def distribute_tasks_on_shift(
        self,
        shift_id: UUID,
    ) -> None:
        """Раздача участникам заданий на 3 месяца.

        Задачи раздаются случайным образом.
        Метод запускается при старте смены.
        """
        task_ids_list = await self.task_service.get_task_ids_list()
        user_ids_list = await self.request_service.get_approved_shift_user_ids(shift_id)
        current_shift = await self.shift_repository.get(shift_id)

        result = []
        for user_id in user_ids_list:
            random.shuffle(task_ids_list)
            all_days = (current_shift.finished_at - current_shift.created_at).days
            all_dates = tuple((current_shift.created_at + timedelta(day)) for day in range(all_days))
            for one_date in all_dates:
                result.append(
                        UserTask(
                            user_id=user_id,
                            shift_id=shift_id,
                            # Task_id на позиции, соответствующей дню месяца.
                            # Например, для первого числа это task_ids[0]
                            task_id=task_ids_list[one_date.day - 1],
                            day=one_date,
                        )
                )  
        await self.user_task_repository.create_all(result)
