from fastapi import Depends
from pydantic.schema import UUID

from src.core.db.repository.task_repository import TaskRepository


class TaskService:
    def __init__(self, task_repository: TaskRepository = Depends()) -> None:
        self.__task_repository = task_repository

    async def get_task_ids_list(
        self,
    ) -> list[UUID]:
        return await self.__task_repository.get_task_ids_list()
