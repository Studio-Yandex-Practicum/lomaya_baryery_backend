import logging
import secrets
import string
import sys
from calendar import calendar
from datetime import date, datetime, timedelta
from random import shuffle

import pytz
from loguru import logger

from src.core.settings import settings


def get_current_task_date() -> datetime.date:
    """Вычислить текущий день задания с учетом времени отправления."""
    now = datetime.now(pytz.timezone(settings.TIME_ZONE))
    return now.date() if now.hour >= settings.SEND_NEW_TASK_HOUR else now.date() - timedelta(days=1)


def add_months(source_date: date, months: int):
    """Добавляет к дате заданное количество месяцев."""
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def generate_password() -> str:
    """Генерация пароля в соответствии с правилами."""
    password_chars = [secrets.choice(string.ascii_uppercase) for _ in range(2)]
    password_chars += [secrets.choice(string.ascii_lowercase) for _ in range(4)]
    password_chars += [secrets.choice(string.digits) for _ in range(2)]
    shuffle(password_chars)
    return ''.join(password_chars)


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


def get_message_with_numbers_attempts(count_attempts: int) -> str:
    """Возвращает правильные словосочетания в зависимости от количества оставшихся попыток для сдачи отчета."""
    if count_attempts == 0:
        return "У тебя не осталось попыток для сдачи отчета."
    if count_attempts == 1:
        extra_text = f"осталась {count_attempts} попытка"
    elif count_attempts > 4:
        extra_text = f"осталось {count_attempts} попыток"
    else:
        extra_text = f"осталось {count_attempts} попытки"
    return f"Ты можешь отправить отчет повторно до {settings.FORMATTED_TASK_TIME} часов утра. У тебя {extra_text}."


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
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    logging.basicConfig(handlers=[InterceptHandler()], level=settings.LOG_LEVEL)

    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
    logger.remove()
    logger.add(sys.stdout, level='INFO')
    logger.add(
        settings.LOG_LOCATION,
        rotation=settings.LOG_ROTATION_TIME,
        compression=settings.LOG_COMPRESSION,
        level=settings.LOG_LEVEL,
    )
    logger.add(
        settings.LOG_ERROR_LOCATION,
        rotation=settings.LOG_ROTATION_TIME,
        compression=settings.LOG_COMPRESSION,
        level=settings.LOG_ERROR_LEVEL,
    )
