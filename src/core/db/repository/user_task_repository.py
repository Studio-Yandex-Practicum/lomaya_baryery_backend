from typing import List, Tuple, Union

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import Shift, User, Task, UserTask


async def get_shift(shift_id: int, session: AsyncSession):
    """Получаем данные смены."""
    shift = await session.execute(
        select(Shift).where(Shift.id == shift_id)
    )
    return shift.scalars().first()


async def get_user_info(user_id: int, session: AsyncSession):
    """Получаем имя и фамилию юзера."""
    user_info = await session.execute(
        select([User.name,
                User.surname])
        .where(User.id == user_id)
    )
    user_info = user_info.all()
    user_info = dict(user_info[0])
    return user_info


async def get_task_info(task_id: int, session: AsyncSession):
    """Получаем ссылку и описание задачи."""
    task_info = await session.execute(
        select([(Task.id).label('task_id'),
                (Task.description).label('task_description'),
                (Task.url).label('task_url')])
        .where(Task.id == task_id)
    )
    task_info = task_info.all()
    task_info = dict(task_info[0])
    return task_info


async def get_user_task_ids(
        shift_id: int,
        day_number: int,
        session: AsyncSession
) -> List[Tuple[int]]:
    """Получаем id всех юзеров и
    id новых или непроверенных задач этих юзеров
    в конкретный день конкретной смены."""
    user_tasks_info = await session.execute(
        select([UserTask.id,
                UserTask.user_id,
                UserTask.task_id])
        .where(and_(UserTask.shift_id == shift_id,
                    UserTask.day_number == day_number,
                    or_(UserTask.status == UserTask.Status.NEW,
                        UserTask.status == UserTask.Status.UNDER_REVIEW)))
        .order_by(UserTask.id)
    )
    user_tasks_ids = user_tasks_info.all()
    return user_tasks_ids
