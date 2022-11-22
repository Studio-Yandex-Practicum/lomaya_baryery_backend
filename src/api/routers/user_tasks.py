from datetime import date
from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, Depends, Path, Request
from fastapi_restful.cbv import cbv
from pydantic.schema import UUID

from src.api.response_models.user_task import (
    UserTaskResponse,
    UserTasksAndShiftResponse,
    UserTaskSummaryResponse,
)
from src.core.db.models import UserTask
from src.core.services.shift_service import ShiftService
from src.core.services.user_task_service import UserTaskService

router = APIRouter(prefix="/user_tasks", tags=["user_tasks"])


@cbv(router)
class UserTasksCBV:
    shift_service: ShiftService = Depends()
    user_task_service: UserTaskService = Depends()

    @router.get(
        "/{user_task_id}",
        response_model=UserTaskResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Получить информацию об отчёте участника.",
        response_description="Полная информация об отчёте участника.",
    )
    async def get_user_report(
        self,
        user_task_id: UUID,
    ) -> dict:
        """Вернуть отчет участника.

        - **user_id**:номер участника
        - **user_task_id**: номер задачи, назначенной участнику на день смены (генерируется рандомно при старте смены)
        - **task_id**: номер задачи
        - **task_date**: дата получения задания
        - **status**: статус задачи
        - **photo_url**: url фото выполненной задачи
        """
        return await self.user_task_service.get_user_task_with_report_url(user_task_id)

    @router.patch(
        "/{user_task_id}/approve",
        status_code=HTTPStatus.OK,
        summary="Принять задание. Будет начислен 1 \"ломбарьерчик\".",
    )
    async def approve_task_status(
        self,
        user_task_id: UUID,
        request: Request,
    ) -> HTTPStatus.OK:
        """Отчет участника проверен и принят."""
        return await self.user_task_service.approve_task(user_task_id, request.app.state.bot_instance.bot)

    @router.patch("/{user_task_id}/decline", status_code=HTTPStatus.OK, summary="Отклонить задание.")
    async def decline_task_status(
        self,
        user_task_id: UUID,
        request: Request,
    ) -> HTTPStatus.OK:
        """Отчет участника проверен и отклонен."""
        return await self.user_task_service.decline_task(user_task_id, request.app.state.bot_instance.bot)

    @router.get(
        "/{shift_id}/{task_date}/new",
        response_model=UserTasksAndShiftResponse,
        summary="Получить непроверенные и новые задания.",
    )
    async def get_new_and_under_review_tasks(
        self,
        shift_id: UUID = Path(..., title="ID смены"),
        task_date: date = Path(..., title="Дата получения задания"),
    ) -> dict[str, Union[dict, list]]:
        """Получить непроверенные и новые задания.

        Запрос информации о непроверенных и новых
        заданиях участников по состоянию на указанный день
        в определенной смене:

        - **shift_id**: уникальный id смены, ожидается в формате UUID.uuid4
        - **task_date**: дата получения задания, формат yyyy mm dd
        """
        shift = await self.shift_service.get_shift(shift_id)
        tasks = await self.user_task_service.get_tasks_report(shift_id, task_date)
        report = dict()
        report["shift"] = shift
        report["tasks"] = tasks
        return report

    @router.get(
        "/",
        response_model=list[UserTaskSummaryResponse],
        summary="Получения списка заданий пользователя по полям status и shift_id.",
    )
    async def get_user_task_summary(
        self,
        shift_id: UUID = None,
        status: UserTask.Status = None,
    ) -> list[UserTaskSummaryResponse]:
        """
        Получения списка задач на проверку с возможностью фильтрации по полям status и shift_id.

        Список формируется по убыванию поля started_at.

        В запросе передаётся:

        - **shift_id**: уникальный id смены, ожидается в формате UUID.uuid4
        - **user_task.status**: статус задачи
        """
        return await self.user_task_service.get_summaries_of_user_tasks(shift_id, status)
