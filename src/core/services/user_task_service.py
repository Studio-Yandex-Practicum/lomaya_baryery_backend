from typing import Any, Union
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Photo, User, Shift, Task, UserTask


class UserTaskService:
    """Вспомогательный класс для UserTask.

    Внутри реализованы методы для формирования итогового
    отчета с информацией о смене и непроверенных задачах пользователей
    с привязкой к смене и дню.

    Для инициализации необходимы параметры:
    session - объект сессии.

    Метод 'get_tasks_report' формирует отчет с информацией о задачах
    и юзерах.
    Метод 'get' возвращает экземпляр UserTask по id.

    Используется для ЭПИКА 'API: список заданий на проверке'
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_all_ids_callback(
            self,
            shift_id,
            day_number,
    ) -> list[tuple[int]]:
        """Получает список кортежей с id всех UserTask, id всех юзеров и id задач этих юзеров."""
        user_tasks_info = await self.session.execute(
            select(UserTask.id,
                   UserTask.user_id,
                   UserTask.task_id)
            .where(and_(UserTask.shift_id == shift_id,
                        UserTask.day_number == day_number,
                        or_(UserTask.status == UserTask.Status.NEW,
                            UserTask.status == UserTask.Status.UNDER_REVIEW
                    )))
            .order_by(UserTask.id)
        )
        user_tasks_ids = user_tasks_info.all()
        return user_tasks_ids

    async def get_tasks_report(self, shift_id, day_number) -> list[dict[str, Any]]:
        """Формирует итоговый список 'tasks' с информацией о задачах и юзерах."""
        ids_list = await self._get_all_ids_callback(shift_id, day_number)
        tasks = []
        if not ids_list:
            return tasks
        for ids in ids_list:
            task_summary_info = await self.session.execute(
                select(User.name,
                       User.surname,
                       Task.id.label('task_id'),
                       Task.description.label('task_description'),
                       Task.url.label('task_url'))
                .select_from(User,
                             Task)
                .where(User.id == ids.user_id,
                       Task.id == ids.task_id)
            )
            task_summary_info = task_summary_info.all()
            task = dict(*task_summary_info)
            task['id'] = ids.id
            tasks.append(task)
        return tasks

    async def get(self, user_task_id: UUID):
        """Получить объект отчета участника по id."""
        user_task = await self.session.execute(
            select(UserTask, Photo.url.label('photo_url'))
            .where(UserTask.id == user_task_id)
        )
        return user_task.scalars().first()


async def get_user_task_service(
        session: AsyncSession = Depends(get_session)
) -> UserTaskService:
    user_task_service = UserTaskService(session)
    return user_task_service
