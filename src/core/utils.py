from datetime import datetime, timedelta

from src.core.settings import settings


def get_current_task_date() -> datetime.date:
    """Вычислить текущий день задания с учетом времени отправления."""
    now = datetime.now()
    return now.date() if now.hour >= settings.SEND_NEW_TASK_HOUR else now.date() - timedelta(days=1)


def get_lombaryers_for_quantity(numbers_lombaryers: int) -> str:
    """Склоняем слово ломбарьерчик в зависимости от кол-ва"""
    plural = 'ломбарьерчиков'
    singular = 'ломбарьерчик'
    genitive = 'ломбарьерчика'
    last_two_digits = numbers_lombaryers % 100
    if 11 <= last_two_digits <= 19:
        return plural
    last_digit = last_two_digits % 10
    if last_digit == 1:
        return singular
    if 1 < last_digit < 5:
        return genitive
    return plural
