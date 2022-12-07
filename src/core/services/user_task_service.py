from datetime import date
from http import HTTPStatus
from typing import Any

from fastapi import Depends, HTTPException
from pydantic.schema import UUID
from telegram.ext import Application

from src.api.request_models.request import Status
from src.api.response_models.task import LongTaskResponse
from src.bot import services
from src.core.db import DTO_models
from src.core.db.models import UserTask
from src.core.db.repository import (
    MemberRepository,
    ShiftRepository,
    TaskRepository,
    UserRepository,
    UserTaskRepository,
)
from src.core.db.repository.request_repository import RequestRepository
from src.core.exceptions import DuplicateReportError
from src.core.services.request_sevice import RequestService
from src.core.services.task_service import TaskService
from src.core.settings import settings

REVIEWED_TASK = "Задание уже проверено, статус задания: {}."
WAIT_REPORT_TASK = "К заданию нет отчета участника, статус задания: {}."


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
        member_repository: MemberRepository = Depends(),
    ) -> None:
        self.__telegram_bot = services.BotService
        self.__user_task_repository = user_task_repository
        self.__task_repository = task_repository
        self.__shift_repository = shift_repository
        self.__task_service = task_service
        self.__request_service = request_service
        self.__request_repository = request_repository
        self.__user_repository = user_repository
        self.__member_repository = member_repository

    async def get_user_task(self, id: UUID) -> UserTask:
        return await self.__user_task_repository.get(id)

    async def get_user_task_with_report_url(self, id: UUID) -> dict:
        return await self.__user_task_repository.get_user_task_with_report_url(id)

    async def check_duplicate_report(self, url: str) -> None:
        user_task = await self.__user_task_repository.get_by_report_url(url)
        if user_task:
            raise DuplicateReportError()

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

    async def approve_report(self, report_id: UUID, bot: Application.bot) -> None:
        """Задание принято: изменение статуса, начисление 1 /"ломбарьерчика/", уведомление участника."""
        user_task = await self.__user_task_repository.get(report_id)
        self.__can_change_status(user_task.status)
        user_task.status = Status.APPROVED
        await self.__user_task_repository.update(report_id, user_task)
        member = await self.__member_repository.get_with_user_info(user_task.member_id)
        member.numbers_lombaryers += 1
        await self.__member_repository.update(member.id, member)
        await self.__telegram_bot(bot).notify_approved_task(member.user.telegram_id, user_task)
        return

    async def decline_report(self, user_task_id: UUID, bot: Application.bot) -> None:
        """Задание отклонено: изменение статуса, уведомление участника в телеграм."""
        user_task = await self.__user_task_repository.get(user_task_id)
        self.__can_change_status(user_task.status)
        user_task.status = Status.DECLINED
        await self.__user_task_repository.update(user_task_id, user_task)
        member = await self.__member_repository.get_with_user_info(user_task.member_id)
        await self.__telegram_bot(bot).notify_declined_task(member.user.telegram_id)
        return

    def __can_change_status(self, status: UserTask.Status) -> None:
        """Уточнение статуса задания."""
        if status in (UserTask.Status.APPROVED, UserTask.Status.DECLINED):
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=REVIEWED_TASK.format(status))
        if status is UserTask.Status.WAIT_REPORT:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=WAIT_REPORT_TASK.format(status))

    async def get_summaries_of_user_tasks(
        self,
        shift_id: UUID,
        status: UserTask.Status,
    ) -> list[DTO_models.FullUserTaskDto]:
        """Получает из БД список отчетов участников.

        Список берется по id смены и/или статусу заданий с url фото выполненного задания.
        """
        return await self.__user_task_repository.get_summaries_of_user_tasks(shift_id, status)

    async def check_members_activity(self, bot: Application.bot) -> None:
        """Проверяет участников во всех запущенных сменах.

        Если участники не посылают отчет о выполненом задании указанное
        в настройках количество раз подряд, то они будут исключены из смены.
        """
        shift_id = await self.__shift_repository.get_started_shift_id()
        user_ids_to_exclude = await self.__user_task_repository.get_members_ids_for_excluding(
            shift_id, settings.SEQUENTIAL_TASKS_PASSES_FOR_EXCLUDE
        )
        if len(user_ids_to_exclude) > 0:
            await self.__request_service.exclude_members(user_ids_to_exclude, shift_id, bot)
            await self.__user_task_repository.set_usertasks_deleted(user_ids_to_exclude, shift_id)

    async def send_report(self, user_id: UUID, photo_url: str) -> UserTask:
        user_task = await self.__user_task_repository.get_current_user_task(user_id)
        await self.check_duplicate_report(photo_url)
        user_task.send_report(photo_url)
        return await self.__user_task_repository.update(user_task.id, user_task)
