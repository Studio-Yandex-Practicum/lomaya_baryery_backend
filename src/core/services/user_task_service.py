import random
from datetime import date, timedelta
from typing import Any

from fastapi import Depends
from pydantic.schema import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.request_models.user_task import ChangeStatusRequest
from src.core.db.db import get_session
from src.core.db.models import UserTask, Shift
from src.core.db.repository import RequestRepository, TaskRepository, UserTaskRepository, ShiftRepository
from src.core.services.request_sevice import RequestService
from src.core.services.shift_service import ShiftService
from src.core.services.task_service import get_task_service


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
    ) -> None:
        self.user_task_repository = user_task_repository
        self.task_repository = task_repository

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
        task_service = await get_task_service(self.session)
        request_service = RequestService(RequestRepository(self.session))
        shift_service = ShiftService(ShiftRepository(self.session))
        task_ids_list = await task_service.get_task_ids_list()
        user_ids_list = await request_service.get_approved_shift_user_ids(shift_id)
        current_shift = await shift_service.get_shift(shift_id)

        def distribution_process(task_ids: list[UUID], shift: Shift, user_id: UUID) -> None:
            """Процесс раздачи заданий пользователю."""
            # Для каждого пользователя
            # случайным образом перемешиваем список task_ids
            random.shuffle(task_ids)
            all_days = (shift.finished_at - shift.created_at).days
            all_dates = tuple((shift.created_at + timedelta(day)) for day in range(all_days))
            for one_date in all_dates:
                new_user_task = UserTask(
                    user_id=user_id,
                    shift_id=shift_id,
                    # Task_id на позиции, соответствующей дню месяца.
                    # Например, для первого числа это task_ids[0]
                    task_id=task_ids[one_date.day - 1],
                    day=one_date,
                )
                self.session.add(new_user_task)

        for userid in user_ids_list:
            distribution_process(task_ids_list, current_shift, userid)

        await self.session.commit()


def get_user_task_service(session: AsyncSession = Depends(get_session)) -> UserTaskService:
    return UserTaskService(session)
