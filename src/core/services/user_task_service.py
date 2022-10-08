from fastapi import Depends
from pydantic.schema import UUID

from src.api.request_models.user_task import ChangeStatusRequest
from src.core.db.models import UserTask
from src.core.db.repository.user_task_repository import UserTaskRepository


class UserTaskService:
    def __init__(self, user_task_repository: UserTaskRepository = Depends()) -> None:
        self.user_task_repository = user_task_repository

    async def get_user_task(self, id: UUID) -> UserTask:
        return await self.user_task_repository.get(id)

    async def get_user_task_with_photo_url(self, id: UUID) -> dict:
        return await self.user_task_repository.get_user_task_with_photo_url(id)

    async def update_status(self, id: UUID, update_user_task_status: ChangeStatusRequest) -> dict:
        await self.user_task_repository.update(id=id, user_task=UserTask(**update_user_task_status.dict()))
        return await self.user_task_repository.get_user_task_with_photo_url(id)
