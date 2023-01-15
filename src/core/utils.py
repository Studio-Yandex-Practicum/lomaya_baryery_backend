import os
from datetime import datetime, timedelta

from src.core.settings import settings


def get_current_task_date() -> datetime.date:
    """Вычислить текущий день задания с учетом времени отправления."""
    now = datetime.now()
    return now.date() if now.hour >= settings.SEND_NEW_TASK_HOUR else now.date() - timedelta(days=1)


def get_task_images() -> list:
    return ((filename, filename) for filename in os.listdir(settings.task_image_dir))
