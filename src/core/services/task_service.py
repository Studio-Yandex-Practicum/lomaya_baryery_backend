from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import Task


async def get_task_info(task_id: UUID, session: AsyncSession) -> dict[str, Any]:
    """Получаем ссылку и описание задачи.

    Используется для ЭПИКА 'API: список заданий на проверке'.
    """
    task_info = await session.execute(
        select(
            [(Task.id).label("task_id"), (Task.description).label("task_description"), (Task.url).label("task_url")]
        ).where(Task.id == task_id)
    )
    task_info = task_info.all()
    task_info = dict(task_info[0])
    return task_info
