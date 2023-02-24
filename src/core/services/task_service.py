from json import loads
from urllib.parse import urljoin

from fastapi import Depends, UploadFile
from pydantic.schema import UUID

from src.api.request_models.task import TaskCreateRequest
from src.core.db.models import Shift, Task
from src.core.db.repository.task_repository import TaskRepository
from src.core.exceptions import TodayTaskNotFoundError
from src.core.settings import settings


class TaskService:
    def __init__(self, task_repository: TaskRepository = Depends()) -> None:
        self.__task_repository = task_repository

    async def __download_file(self, file: UploadFile) -> str:
        file_name = file.filename.replace(' ', '_')
        with open((settings.task_image_dir / file_name), 'wb') as image:
            image.write(file.file.read())
            image.close()
        return urljoin(settings.task_image_url, file_name)

    async def get_task_ids_list(
        self,
    ) -> list[UUID]:
        return await self.__task_repository.get_task_ids_list()

    async def get_task_by_day_of_month(self, tasks: Shift.tasks, day_of_month: int) -> Task:
        task_id = loads(tasks).get(str(day_of_month))
        task = await self.__task_repository.get_or_none(task_id)
        if not task:
            raise TodayTaskNotFoundError()
        return task

    async def create_task(self, new_task: TaskCreateRequest) -> Task:
        task = Task(description=new_task.description)
        task.url = await self.__download_file(new_task.image)
        return await self.__task_repository.create(instance=task)

    async def get_task(self, id: UUID) -> Task:
        return await self.__task_repository.get(id)

    async def get_all_tasks(self) -> list[Task]:
        return await self.__task_repository.get_all()
