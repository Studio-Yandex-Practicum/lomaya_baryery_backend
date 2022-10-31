import random
from datetime import date, timedelta
from typing import Any

from fastapi import Depends
from pydantic.schema import UUID

from src.api.request_models.user_task import ChangeStatusRequest
from src.core.db.models import UserTask
from src.core.db.repository import ShiftRepository, TaskRepository, UserTaskRepository
from src.core.services.request_sevice import RequestService
from src.core.services.task_service import TaskService
from src.core.settings import settings


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
        shift_repository: ShiftRepository = Depends(),
        task_service: TaskService = Depends(),
        request_service: RequestService = Depends(),
    ) -> None:
        self.__user_task_repository = user_task_repository
        self.__task_repository = task_repository
        self.__shift_repository = shift_repository
        self.__task_service = task_service
        self.__request_service = request_service

    async def get_user_task(self, id: UUID) -> UserTask:
        return await self.__user_task_repository.get(id)

    async def get_user_task_with_photo_url(self, id: UUID) -> dict:
        return await self.__user_task_repository.get_user_task_with_photo_url(id)

    # TODO переписать
    async def get_tasks_report(self, shift_id: UUID, task_date: date) -> list[dict[str, Any]]:
        """Формирует итоговый список 'tasks' с информацией о задачах и юзерах."""
        user_task_ids = await self.__user_task_repository.get_all_ids(shift_id, task_date)
        tasks = []
        if not user_task_ids:
            return tasks
        for user_task_id, user_id, task_id in user_task_ids:
            task = await self.__task_repository.get_tasks_report(user_id, task_id)
            task["id"] = user_task_id
            tasks.append(task)
        return tasks

    async def update_status(self, id: UUID, update_user_task_status: ChangeStatusRequest) -> dict:
        await self.__user_task_repository.update(id=id, user_task=UserTask(**update_user_task_status.dict()))
        return await self.__user_task_repository.get_user_task_with_photo_url(id)

    # TODO переписать
    async def distribute_tasks_on_shift(
        self,
        shift_id: UUID,
    ) -> None:
        """Раздача участникам заданий на 3 месяца.

        Задачи раздаются случайным образом.
        Метод запускается при старте смены.
        """
        current_shift = await self.__shift_repository.get(shift_id)
        task_ids_list = await self.__task_service.get_task_ids_list()
        user_ids_list = await self.__request_service.get_approved_shift_user_ids(shift_id)

        result = []
        for user_id in user_ids_list:
            random.shuffle(task_ids_list)
            number_days = (current_shift.finished_at - current_shift.created_at).days
            all_dates = tuple((current_shift.created_at + timedelta(day)) for day in range(number_days))
            for one_date in all_dates:
                result.append(
                    UserTask(
                        user_id=user_id,
                        shift_id=shift_id,
                        task_id=task_ids_list[one_date.day - 1],
                        task_date=one_date,
                    )
                )
        await self.__user_task_repository.create_all(result)

    async def check_user_activity(self, user_id: UUID) -> bool:
        """Проверяет пропускает ли участник подряд отправку отчета к полученным заданиям.

        Аргументы:
            user_id (UUID): id участника смены

        Возвращает:
            bool: True если пропущено указанное в настройках количество заданий,
            False - если в допустимых пределах.
        """
        today = date.today()
        status = UserTask.Status.WAIT_REPORT
        status_count = await self.__user_task_repository.get_user_last_tasks_status_count(
            user_id, today, settings.TASKS_SKIPPED_IN_ROW_FOR_BAN, status
        )
        return status_count >= settings.TASKS_SKIPPED_IN_ROW_FOR_BAN
