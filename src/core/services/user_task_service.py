from typing import Any, Union
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import UserTask
from src.core.services import get_shift, get_task_info, get_user_info


class UserTaskService:
    """Вспомогательный класс для UserTask.

    Внутри реализованы методы для формирования итогового
    отчета с информацией о смене и непроверенных задачах пользователей
    с привязкой к смене и дню.

    Для инициализации необходимы параметры:
    shift_id - уникальный id смены,
    day_number - номер дня смены,
    db_model - модель UserTask.

    Метод 'get_report' вызывается для формирования отчета.

    Используется для ЭПИКА 'API: список заданий на проверке'
    """

    def __init__(self, shift_id: UUID, day_number: int, db_model: UserTask):
        self._tasks = []
        self._report = {}
        self.shift_id = shift_id
        self.day_number = day_number
        self.model = db_model

    async def _get_all_ids_callback(self, session: AsyncSession) -> list[tuple[int]]:
        """Получает список кортежей с id всех UserTask, id всех юзеров и id задач этих юзеров."""
        user_tasks_info = await session.execute(
            select([self.model.id, self.model.user_id, self.model.task_id])
            .where(
                and_(
                    self.model.shift_id == self.shift_id,
                    self.model.day_number == self.day_number,
                    or_(
                        self.model.status == self.model.Status.NEW, self.model.status == self.model.Status.UNDER_REVIEW
                    ),
                )
            )
            .order_by(self.model.id)
        )
        user_tasks_ids = user_tasks_info.all()
        return user_tasks_ids

    async def _get_summary_tasks_info_callback(self, session: AsyncSession) -> list[dict[str, Any]]:
        """Формирует итоговый список 'tasks' с информацией о задачах и юзерах."""
        ids_list = await self._get_all_ids_callback(session)
        if not ids_list:
            return self._tasks
        for ids in ids_list:
            user_info = await get_user_info(ids.user_id, session)
            task_info = await get_task_info(ids.task_id, session)
            task = {"id": ids.id, **user_info, **task_info}
            self._tasks.append(task)
        return self._tasks

    async def get_report(self, session: AsyncSession) -> dict[str, Union[dict, list]]:
        """Формирует итоговый ответ с информацией о смене и итоговым списком задач и юзеров."""
        shift = await get_shift(self.shift_id, session)
        tasks = await self._get_summary_tasks_info_callback(session)
        self._report["shift"] = shift
        self._report["tasks"] = tasks
        return self._report
