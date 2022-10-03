from fastapi import Depends
from pydantic.schema import UUID

from src.api.request_models.user_task import ChangeStatusRequest
from src.core.db.models import UserTask
from src.core.db.repository import PhotoRepository, UserTaskRepository


class UserTaskService:
    def __init__(
        self, user_task_repository: UserTaskRepository = Depends(), photo_repository: PhotoRepository = Depends()
    ) -> None:
        self.user_task_repository = user_task_repository
        self.photo_repository = photo_repository

    async def get(self, id: UUID):
        user_task = await self.user_task_repository.get(id)
        photo = await self.photo_repository.get(id=user_task.photo_id)
        photo_url = photo.url

        return user_task, photo_url

    async def update_status(self, status: UserTask.Status, update_user_task_status: ChangeStatusRequest) -> UserTask:
        return await self.user_task_repository.update_status(
            status=status, user_task=UserTask(**update_user_task_status.dict())
        )
