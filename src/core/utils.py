import asyncio
from datetime import datetime, timedelta
from typing import Coroutine

from src.core.settings import settings


def get_current_task_date() -> datetime.date:
    """Вычислить текущий день задания с учетом времени отправления."""
    now = datetime.now()
    return now.date() if now.hour >= settings.SEND_NEW_TASK_HOUR else now.date() - timedelta(days=1)


async def run_send_message_tasks(tasks: list[Coroutine], chunk_size: int = 20, sleep_time: int = 2) -> None:
    """Запустить задачи (корутины) по рассылке сообщений из списка.

    Задачи запускаются группами по <chunk_size> шт., с задержкой между группами по <sleep_time> секунд.
    Аргументы:
        tasks (list[Coroutine]) - список задач в виде awaitable объектов (корутины)
        chunk_size (int) - размер групп, на которые разделяется список задач
        sleep_time (int) - задержка рассылки между группами задач, в секундах.
    """
    for i in range(0, len(tasks), chunk_size):
        await asyncio.gather(*tasks[i:i + chunk_size])
        await asyncio.sleep(sleep_time)
