from fastapi import Depends
from pydantic.schema import UUID

from src.api.request_models.task import TaskCreateUpdateRequest
from src.api.response_models.task import TaskResponse
from src.core.db.models import Shift, Task
from src.core.db.repository.task_repository import TaskRepository
from src.core.exceptions import TodayTaskNotFoundError


class TaskService:
    def __init__(self, task_repository: TaskRepository = Depends()) -> None:
        self.__task_repository = task_repository

    async def get_task_ids_list(
        self,
    ) -> list[UUID]:
        return await self.__task_repository.get_task_ids_list()

    async def get_task_by_day_of_month(self, tasks: Shift.tasks, day_of_month: int) -> Task:
        task_id = tasks.get(str(day_of_month))
        task = await self.__task_repository.get_or_none(task_id)
        if not task:
            raise TodayTaskNotFoundError()
        return task

    async def create_new_task(self, new_task: TaskCreateUpdateRequest) -> Task:
        task = Task(**new_task.dict())
        return await self.__task_repository.create(instance=task)

    async def update_task(self, id: UUID, update_task_data: TaskCreateUpdateRequest) -> Task:
        task: Task = await self.__task_repository.get(id)
        task.url = update_task_data.url
        task.description = update_task_data.description
        return await self.__task_repository.update(id, task)

    async def get_task(self, id: UUID) -> Task:
        return await self.__task_repository.get(id)

    async def list_all_tasks(self) -> list[TaskResponse]:
        return await self.__task_repository.get_tasks()
