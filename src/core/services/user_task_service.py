from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.repository.user_task_repository import (get_shift,
                                                         get_user_info,
                                                         get_task_info,
                                                         get_user_task_ids)


async def get_summary_list_tasks_info(user_tasks_ids: List, session: AsyncSession):
    """Формируем итоговый список с информацией о задачах и юзерах."""
    if not user_tasks_ids:
        return []
    tasks = []
    for ids in user_tasks_ids:
        user_info = await get_user_info(ids['user_id'], session)
        task_info = await get_task_info(ids['task_id'], session)
        task = {'id': ids['id'], **user_info, **task_info}
        tasks.append(task)
    return tasks


async def get_summary_user_tasks_response(
        shift_id: int,
        day_number: int,
        session: AsyncSession
):
    """Формируем итоговый ответ с информацией
    о смене и итоговым списком задач и юзеров."""
    shift = await get_shift(shift_id, session)
    user_task_ids = await get_user_task_ids(shift_id, day_number, session)
    tasks = await get_summary_list_tasks_info(user_task_ids, session)
    return {'shift': shift, 'tasks': tasks}
