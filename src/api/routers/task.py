from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv

from src.api.request_models.task import TaskCreateUpdateRequest
from src.api.response_models.task import TaskResponse
from src.core.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Task"])


@cbv(router)
class TaskCBV:
    task_service: TaskService = Depends()

    @router.post(
        "/",
        response_model=TaskResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.CREATED,
        summary="Создать новое задание",
        response_description="Информация о созданном задании",
    )
    async def create_new_task(
        self,
        task: TaskCreateUpdateRequest,
    ) -> TaskResponse:
        """
        Создать новое задание.

        - **description**: описание задания
        """
        return await self.task_service.create_new_task(task)

    @router.patch(
        "/{task_id}",
        response_model=TaskResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Обновить задание",
        response_description="Обновленная информация о задании",
    )
    async def update_task(
        self,
        task_id: UUID,
        update_task_data: TaskCreateUpdateRequest,
    ) -> TaskResponse:
        """
        Обновить задание.

        - **description**: описание задания
        """
        return await self.task_service.update_task(task_id, update_task_data)

    @router.get(
        "/",
        response_model=list[TaskResponse],
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Получить список заданий",
        response_description="Информация о заданиях",
    )
    async def get_all_tasks(self) -> list[TaskResponse]:
        """
        Получить список заданий.

        - **id**: id задания
        - **url**: url задания
        - **description**: описание задания
        """
        return await self.task_service.list_all_tasks()

    @router.get(
        "/{task_id}",
        response_model=TaskResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Получить задание",
        response_description="Информация о задании",
    )
    async def get_task(
        self,
        task_id: UUID,
    ) -> TaskResponse:
        """
        Получить задание.

        - **id**: id задания
        - **url**: url задания
        - **description**: описание задания
        """
        return await self.task_service.get_task(task_id)
