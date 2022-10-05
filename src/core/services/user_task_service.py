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

    async def get_user_task_photo(self, id: UUID) -> UserTask:
        return await self.user_task_repository.get(id)

    async def update_status(self, id: UUID, update_user_task_status: ChangeStatusRequest) -> UserTask:
        return await self.user_task_repository.update_status(id=id, status=update_user_task_status.status)
