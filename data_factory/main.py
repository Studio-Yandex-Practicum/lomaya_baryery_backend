import logging

import sys

import click
import factory
from sqlalchemy import select, func

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from data_factory.factories import (SESSION, UserFactory,
                                    ShiftFactory, PhotoFactory, TaskFactory, RequestFactory)

from src.core.db.models import Shift, User, Request


def get_logger(log_filename: str) -> logging.Logger:
    file_handler = logging.FileHandler(filename=f'data_factory/{log_filename}', encoding='utf-8')
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    handlers = [file_handler, stdout_handler]
    format = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
    name = 'fill_db_log'
    logging.basicConfig(level=logging.INFO, handlers=handlers, format=format)
    return logging.getLogger(name)


logger = get_logger('fill_db.log')


def get_random_user_ids(count: int) -> list:
    user_ids = SESSION.execute(select(User.id).order_by(func.random()).limit(count))
    user_ids = user_ids.scalars().all()
    return user_ids


def truncate_tables(session: Session) -> None:
    """Очистить таблицы БД."""
    logger.info("Удаление данных из таблиц...")
    session.execute("""TRUNCATE TABLE photos, requests, shifts, tasks, user_tasks, users""")
    session.commit()


def generate_fake_data() -> None:
    logger.info("Генерация фейковых данных...")
    with factory.Faker.override_default_locale("ru_RU"):

        logger.info("Создание пользователей...")
        UserFactory.create_batch(200)

        logger.info("Создание заданий...")
        TaskFactory.create_batch(31)

        logger.info("Создание фотографий...")
        PhotoFactory.create_batch(10)

        logger.info("Создание активной смены...")
        started_shift = ShiftFactory.create(status=Shift.Status.STARTED)
        user_ids = get_random_user_ids(30)

        logger.info("Создание одобренных заявок и заданий для активной смены...")
        for user_id in user_ids[:15]:
            RequestFactory.complex_create(1, user_id=user_id, shift_id=started_shift.id,
                                          status=Request.Status.APPROVED)

        logger.info("Создание отклоненных заявок для активной смены...")
        for user_id in user_ids[15:]:
            RequestFactory.create(user_id=user_id, shift_id=started_shift.id,
                                  status=Request.Status.DECLINED)

        logger.info("Создание завершенной смены...")
        finished_shifts = ShiftFactory.create_batch(2, status=Shift.Status.FINISHED)
        for finished_shift in finished_shifts:
            user_ids = get_random_user_ids(30)

            logger.info("Создание одобренных заявок и заданий для завершенной смены...")
            for user_id in user_ids[:15]:
                RequestFactory.complex_create(1, user_id=user_id, shift_id=finished_shift.id,
                                              status=Request.Status.APPROVED)

            logger.info("Создание отклоненных заявок для завершенной смены...")
            for user_id in user_ids[15:]:
                RequestFactory.create(user_id=user_id, shift_id=finished_shift.id,
                                      status=Request.Status.DECLINED)

        logger.info("Создание новой смены...")
        ShiftFactory.create(status=Shift.Status.PREPARING)

    logger.info("Создание тестовых данных завершено!")


@click.command()
@click.option('--delete', is_flag=True, help="Удаление существующих данных из таблиц")
def fill_command(delete) -> None:
    if delete:
        msg = (
            "ВНМАНИЕ! Дальнейшее действие приведет к удалению ВСЕХ существующих данных из ВСЕХ таблиц БД!\n"
            "Продолжить? (y/n): "
        )
        if input(msg).lower().strip() not in ("y", "yes"):
            return
        truncate_tables(SESSION)
        generate_fake_data()
    else:
        try:
            generate_fake_data()
        except IntegrityError:
            logger.error("Повторное наполнение БД тестовыми данными не предусмотрено!")


if __name__ == "__main__":
    fill_command()
