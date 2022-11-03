from pydantic.schema import UUID

from src.core.db.repository.task_repository import TaskRepository, task_repository


class TaskService:
    def __init__(self, task_repository: TaskRepository = task_repository) -> None:
        self.__task_repository = task_repository

    async def get_task_ids_list(self) -> list[UUID]:
        return await self.__task_repository.get_task_ids_list()
