import random

from fastapi import Depends
from pydantic.schema import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Photo, UserTask
from src.core.services.request_service import get_request_service
from src.core.services.task_service import get_task_service


class UserTaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(
        self,
        user_task_id: UUID,
    ):
        """Получить объект отчета участника по id."""
        user_task = await self.session.execute(
            select(UserTask, Photo.url.label("photo_url")).where(UserTask.id == user_task_id)
        )
        return user_task.scalars().first()

    async def distribute_tasks_on_shift(
        self,
        shift_id: UUID,
    ) -> None:
        """Раздача участникам заданий на 3 месяца.

        Задачи раздаются случайным образом.
        Метод запускается при старте смены.
        """
        task_service = await get_task_service(self.session)
        request_service = await get_request_service(self.session)
        task_ids = await task_service.get_task_ids_list()
        user_ids = await request_service.get_user_ids_approved_to_shift(shift_id)

        for user_id in user_ids:
            # Случайным образом перемешиваем список task_ids
            random.shuffle(task_ids)
            task_counter = 0
            for day in range(1, 94):

                new_user_task = UserTask(
                    user_id=user_id,
                    shift_id=shift_id,
                    task_id=task_ids[task_counter],
                    day_number=day,
                )
                self.session.add(new_user_task)
                task_counter += 1
                if task_counter == len(task_ids):
                    task_counter = 0
        await self.session.commit()


async def get_user_task_service(session: AsyncSession = Depends(get_session)) -> UserTaskService:
    user_task_service = UserTaskService(session)
    return user_task_service
