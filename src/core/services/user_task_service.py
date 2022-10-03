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

    Метод 'get_tasks_report' формирует отчет с информацией о задачах
    и юзерах.
    Метод 'get' возвращает экземпляр UserTask по id.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_all_ids_callback(
            self,
            shift_id: UUID,
            day_number: int,
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

    async def get_tasks_report(
            self,
            shift_id: UUID,
            day_number: int
    ) -> list[dict[str, Any]]:
        """Формирует итоговый список 'tasks' с информацией о задачах и юзерах."""
        user_task_ids = await self._get_all_ids_callback(shift_id, day_number)
        tasks = []
        if not user_task_ids:
            return tasks
        for user_task_id, user_id, task_id in user_task_ids:
            task_summary_info = await self.session.execute(
                select(User.name,
                       User.surname,
                       Task.id.label('task_id'),
                       Task.description.label('task_description'),
                       Task.url.label('task_url'))
                .select_from(User,
                             Task)
                .where(User.id == user_id,
                       Task.id == task_id)
            )
            task_summary_info = task_summary_info.all()
            task = dict(*task_summary_info)
            task['id'] = user_task_id
            tasks.append(task)
        return tasks

    async def get_or_none(
        self,
        user_task_id: UUID,
    ) -> UserTask:
        """Получить объект отчета участника по id."""
        user_task = await self.session.execute(
            select(UserTask, Photo.url.label("photo_url")).where(UserTask.id == user_task_id)
        )
        return user_task.scalars().first()

    async def change_status(
        self,
        user_task: UserTask,
        status: UserTask.Status,
    ) -> UserTask:
        """Изменить статус задачи."""
        user_task.status = status
        self.session.add(user_task)
        await self.session.commit()
        await self.session.refresh(user_task)
        return user_task


def get_user_task_service(session: AsyncSession = Depends(get_session)) -> UserTaskService:
    return UserTaskService(session)
