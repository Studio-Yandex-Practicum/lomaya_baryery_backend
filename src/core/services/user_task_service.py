import random
from datetime import date, timedelta
from http import HTTPStatus
from typing import Any

from fastapi import Depends, HTTPException
from pydantic.schema import UUID

from src.api.request_models.request import Status
from src.api.response_models.task import LongTaskResponse
from src.bot import services
from src.core.db.DTO_models import DataForStatusByShiftDB
from src.core.db.models import UserTask
from src.core.db.repository import (
    ShiftRepository,
    TaskRepository,
    UserRepository,
    UserTaskRepository,
)
from src.core.db.repository.request_repository import RequestRepository
from src.core.services.request_sevice import RequestService
from src.core.services.task_service import TaskService

REVIEWED_TASK = "Задание уже проверено, статус задания: {}."
WAIT_REPORT_TASK = "К заданию нет отчета участника, статус задания: {}."
NEW_TASK = "Задание не было отправлено участнику, статус задания: {}."


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
        request_repository: RequestRepository = Depends(),
        user_repository: UserRepository = Depends(),
    ) -> None:
        self.__telegram_bot = services.BotService()
        self.__user_task_repository = user_task_repository
        self.__task_repository = task_repository
        self.__shift_repository = shift_repository
        self.__task_service = task_service
        self.__request_service = request_service
        self.__request_repository = request_repository
        self.__user_repository = user_repository

    async def get_user_task(self, id: UUID) -> UserTask:
        return await self.__user_task_repository.get(id)

    async def get_user_task_with_photo_url(self, id: UUID) -> dict:
        return await self.__user_task_repository.get_user_task_with_photo_url(id)

    async def get_today_active_usertasks(self) -> list[LongTaskResponse]:
        usertask_ids = await self.__shift_repository.get_today_active_user_task_ids()
        return await self.__user_task_repository.get_tasks_by_usertask_ids(usertask_ids)

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

    async def approve_task(self, task_id: UUID) -> None:
        """Задание принято: изменение статуса, начисление 1 /"ломбарьерчика/", уведомление участника."""
        user_task = await self.__user_task_repository.get(task_id)
        await self.__check_task_status(user_task.status)
        user_task.status = Status.APPROVED
        await self.__user_task_repository.update(task_id, user_task)
        request = await self.__request_repository.get_by_user_and_shift(user_task.user_id, user_task.shift_id)
        await self.__request_repository.add_one_lombaryer(request)
        await self.__telegram_bot.notify_approved_task(user_task)
        return

    async def decline_task(self, task_id: UUID) -> None:
        """Задание отклонено: изменение статуса, уведомление участника в телеграм."""
        user_task = await self.__user_task_repository.get(task_id)
        await self.__check_task_status(user_task.status)
        user_task.status = Status.DECLINED
        await self.__user_task_repository.update(task_id, user_task)
        await self.__telegram_bot.notify_declined_task(user_task.user.telegram_id)
        return

    async def __check_task_status(self, status: str) -> None:
        """Уточнение статуса задания."""
        if status in (UserTask.Status.APPROVED, UserTask.Status.DECLINED):
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=REVIEWED_TASK.format(status))
        if status is UserTask.Status.NEW:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=NEW_TASK.format(status))

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

    async def get_user_task_by_shift_id_and_status(
        self, shift_id: UUID, status: UserTask.Status
    ) -> list[DataForStatusByShiftDB]:
        return await (
            self.__user_task_repository
            .get_user_tasks_by_shift_id_and_status(shift_id, status)
        )
