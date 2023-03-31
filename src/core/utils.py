import logging
import os
import threading
import zipfile
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


def rotate_logs():
    """Сжатие и удаление старых логов."""
    for root, dirs, files in os.walk(r"./logs"):
        for file in files:
            if file.endswith(".log"):
                with zipfile.ZipFile(
                    f'logs/{file.rstrip(".log")}.zip', mode='w', compression=zipfile.ZIP_DEFLATED
                ) as zf:
                    zf.write(f'logs/{file}')
                    os.remove(f'logs/{file}')


def setup_logging():
    """Установка и настройка логера loguru."""
    x = datetime.today()
    #  Новый лог создается в 12 часов следующего дня
    y = x.replace(day=x.day, hour=12, minute=0, second=0, microsecond=0) + timedelta(days=1)
    delta_t = y - x
    secs = delta_t.total_seconds()
    threading.Timer(secs, setup_logging).start()
    rotate_logs()

    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel("WARNING")

    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    today = datetime.now().strftime("%Y-%m-%d %h-%m-%s")
    logger.level("WARNING")
    logger.configure(
        handlers=[
            {
                "sink": f"logs/{today}.log",
            }
        ]
    )
