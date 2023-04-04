import logging

# import os
# import threading
# import zipfile
from datetime import datetime, timedelta

from loguru import logger

from src.core.settings import settings


def get_current_task_date() -> datetime.date:
    """Вычислить текущий день задания с учетом времени отправления."""
    now = datetime.now()
    return now.date() if now.hour >= settings.SEND_NEW_TASK_HOUR else now.date() - timedelta(days=1)


def get_lombaryers_for_quantity(numbers_lombaryers: int) -> str:
    """Склоняем слово ломбарьерчик в зависимости от кол-ва."""
    PLURAL = 'ломбарьерчиков'  # noqa
    SINGULAR = 'ломбарьерчик'  # noqa
    GENITIVE = 'ломбарьерчика'  # noqa
    last_two_digits = numbers_lombaryers % 100
    if 11 <= last_two_digits <= 19:
        return PLURAL
    last_digit = last_two_digits % 10
    if last_digit == 1:
        return SINGULAR  # noqa
    if 1 < last_digit < 5:
        return GENITIVE  # noqa
    return PLURAL


class InterceptHandler(logging.Handler):
    """Класс для перехвата логов для loguru."""

    def emit(self, record):
        # Получаем соответствущий уровень логов
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Проверяем, откуда получено сообщение
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        if level in ['WARNING', 'ERROR', 'CRITICAL']:
            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel("WARNING")

    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
    logger.add(
        f"logs/{datetime.now().strftime('%Y-%m-%d')}.log", rotation="12:00", compression="tar.gz", level="WARNING"
    )
