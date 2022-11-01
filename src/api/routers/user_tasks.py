from datetime import date
from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, Depends, Path
from fastapi_restful.cbv import cbv
from pydantic.schema import UUID

from src.api.request_models.request import Status
from src.api.response_models.user_task import (
    UserTaskResponse,
    UserTasksAndShiftResponse,
)
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
        user_task = await self.user_task_service.get_user_task_with_photo_url(user_task_id)
        return user_task

    @router.patch(
        "/{user_task_id}/accept",
        status_code=HTTPStatus.OK,
        summary="Принять задание. Будет начислен 1 \"ломбарьерчик\".",
    )
    async def accepted_status_report(
        self,
        user_task_id: UUID,
    ) -> HTTPStatus.OK:
        """Отчет участника проверен и принят."""
        return await self.user_task_service.update_status(user_task_id, Status.APPROVED)

    @router.patch("/{user_task_id}/decline", status_code=HTTPStatus.OK, summary="Отклонить задание.")
    async def declined_status_report(
        self,
        user_task_id: UUID,
    ) -> HTTPStatus.OK:
        """Отчет участника проверен и отклонен."""
        return await self.user_task_service.update_status(user_task_id, Status.DECLINED)

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
