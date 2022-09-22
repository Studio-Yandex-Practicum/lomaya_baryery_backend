import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db.models import Task, User, UserTask


async def task_distribution(
        shift_id: int,
        session: AsyncSession,
):
    """Раздача участникам заданий на 31 день, по три раза (на 3 месяца)
    Задачи раздаются случайным образом. Метод запускается при старте смены.
    """
    user_ids = await session.execute(
        select(
            User.id
        )
    )
    task_ids = await session.execute(
        select(
            Task.id
        )
    )
    user_ids = user_ids.scalars().all()
    task_ids = task_ids.scalars().all()

    for user_id in user_ids:
        # Случайным образом перемешиваем список task_ids
        random.shuffle(task_ids)
        task_counter = 0
        # Повторяем три раза для смены в три месяца
        for _ in range(3):
            for day in range(1, 32):

                new_user_task = UserTask(
                    user_id=user_id,
                    shift_id=shift_id,
                    task_id=task_ids[task_counter],
                    day_number=day,
                )
                session.add(new_user_task)
            task_counter += 1
    await session.commit()
