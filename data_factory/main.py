import logging
import random
import sys
from datetime import timedelta

import click
import factory

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from data_factory.factories import (SESSION, RequestFactory,
                                    UserTaskFactory, UserFactory,
                                    ShiftFactory, PhotoFactory, TaskFactory, STARTED_SHIFT_DURATION)

from src.core.db.models import User, Task, UserTask, Request, Shift

FAKE_USERS_COUNT = 200
FAKE_TASK_COUNT = 31
FAKE_PHOTO_COUNT = 10
FAKE_FINISHED_SHIFTS_COUNT = 1
FAKE_TOTAL_REQUESTS_IN_SHIFT = random.randrange(30, 60)
FAKE_REQUESTS_DECLINED_COUNT = range(2)
FAKE_REQUESTS_EXCLUDED_COUNT = range(2, 4)
FAKE_REQUESTS_APPROVED_COUNT = range(4, FAKE_TOTAL_REQUESTS_IN_SHIFT)
STATUS_REQUESTS_COUNT = {
    Request.Status.DECLINED: FAKE_REQUESTS_DECLINED_COUNT,
    Request.Status.EXCLUDED: FAKE_REQUESTS_EXCLUDED_COUNT,
    Request.Status.APPROVED: FAKE_REQUESTS_APPROVED_COUNT
}

FAKE_PREPARING_REQUESTS_DECLINED_COUNT = range(2)
FAKE_PREPARING_REQUESTS_APPROVED_COUNT = range(2, FAKE_TOTAL_REQUESTS_IN_SHIFT)
STATUS_PREPARING_REQUESTS_COUNT = {
    Request.Status.DECLINED: FAKE_REQUESTS_DECLINED_COUNT,
    Request.Status.APPROVED: FAKE_REQUESTS_APPROVED_COUNT
}


def get_logger(log_filename: str) -> logging.Logger:
    file_handler = logging.FileHandler(filename=f'data_factory/{log_filename}', encoding='utf-8')
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    handlers = [file_handler, stdout_handler]
    format = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
    name = 'fill_db_log'
    logging.basicConfig(level=logging.INFO, handlers=handlers, format=format)
    return logging.getLogger(name)


logger = get_logger('fill_db.log')


def generate_started_shifts(task_ids_list: list) -> None:
    logger.info("Заполнение данными для активной смены...")
    started_shift = ShiftFactory.create(status=Shift.Status.STARTED)
    user_ids = SESSION.execute(select(User.id).order_by(func.random()).limit(FAKE_TOTAL_REQUESTS_IN_SHIFT))
    user_ids = user_ids.scalars().all()

    logger.info("Создание заявок для активной смены...")
    for status, count in STATUS_REQUESTS_COUNT.items():
        for i in count:
            RequestFactory.create(status=status, user_id=user_ids[i], shift_id=started_shift.id)
    user_ids = SESSION.execute(select(Request.user_id).where(
        Request.status == Request.Status.APPROVED, Request.shift_id == started_shift.id)
    )
    logger.info("Создание создание заданий для участников активной смены...")
    user_ids = user_ids.scalars().all()
    number_days = (started_shift.finished_at - started_shift.started_at).days
    all_dates = tuple((started_shift.started_at + timedelta(day)) for day in range(number_days))
    for user_id in user_ids:
        for one_date in all_dates[:STARTED_SHIFT_DURATION]:
            UserTaskFactory.create(
                task_id=task_ids_list[one_date.day - 1],
                user_id=user_id,
                shift_id=started_shift.id,
                task_date=one_date,
                status=UserTask.Status.APPROVED
            )
            user = SESSION.execute(select(User).where(User.id == user_id))
            user = user.scalars().first()
            user.numbers_lombaryers += 1
        UserTaskFactory.create(
            task_id=task_ids_list[one_date.day - 1],
            user_id=user_id,
            shift_id=started_shift.id,
            task_date=all_dates[STARTED_SHIFT_DURATION],
            status=UserTask.Status.UNDER_REVIEW
        )
        for one_date in all_dates[STARTED_SHIFT_DURATION + 1:]:
            UserTaskFactory.create(
                task_id=task_ids_list[one_date.day - 1],
                user_id=user_id,
                shift_id=started_shift.id,
                task_date=one_date,
                status=UserTask.Status.NEW
            )


def generate_preparing_shifts() -> None:
    logger.info("Заполнение данными для новой смены...")
    preparing_shift = ShiftFactory.create(status=Shift.Status.PREPARING)
    user_ids = SESSION.execute(select(User.id).order_by(func.random()).limit(FAKE_TOTAL_REQUESTS_IN_SHIFT))
    user_ids = user_ids.scalars().all()
    logger.info("Создание заявок для новой смены")
    for status, count in STATUS_REQUESTS_COUNT.items():
        for i in count:
            RequestFactory.create(status=status, user_id=user_ids[i], shift_id=preparing_shift.id)


def generate_finished_shifts(task_ids_list: list) -> None:
    logger.info("Заполнение данными для завершенных смен...")
    finished_shifts = ShiftFactory.create_batch(FAKE_FINISHED_SHIFTS_COUNT, status=Shift.Status.FINISHED)
    for finished_shift in finished_shifts:
        user_ids = SESSION.execute(select(User.id).order_by(func.random()).limit(FAKE_TOTAL_REQUESTS_IN_SHIFT))
        user_ids = user_ids.scalars().all()
        logger.info("Создание заявок для завершенных смен...")
        for status, count in STATUS_REQUESTS_COUNT.items():
            for i in count:
                RequestFactory.create(status=status, user_id=user_ids[i], shift_id=finished_shift.id)
        user_ids = SESSION.execute(select(Request.user_id).where(
            Request.status == Request.Status.APPROVED, Request.shift_id == finished_shift.id)
        )
        user_ids = user_ids.scalars().all()
        number_days = (finished_shift.finished_at - finished_shift.started_at).days
        all_dates = tuple((finished_shift.started_at + timedelta(day)) for day in range(number_days))
        logger.info("Создание заданий для участников завершенных смен...")
        for user_id in user_ids:
            for one_date in all_dates[:2]:
                UserTaskFactory.create(
                    task_id=task_ids_list[one_date.day - 1],
                    user_id=user_id,
                    shift_id=finished_shift.id,
                    task_date=one_date,
                    status=UserTask.Status.DECLINED
                )
            for one_date in all_dates[3:]:
                UserTaskFactory.create(
                    task_id=task_ids_list[one_date.day - 1],
                    user_id=user_id,
                    shift_id=finished_shift.id,
                    task_date=one_date,
                    status=UserTask.Status.APPROVED
                )
                user = SESSION.execute(select(User).where(User.id == user_id))
                user = user.scalars().first()
                user.numbers_lombaryers = 0
                user.numbers_lombaryers += 1


def truncate_tables(session: Session) -> None:
    """Очистить таблицы БД."""
    msg = (
        "ВНМАНИЕ! Дальнейшее действие приведет к удалению ВСЕХ существующих данных из ВСЕХ таблиц БД!\n"
        "Продолжить? (y/n): "
    )
    if input(msg).lower().strip() not in ("y", "yes"):
        return
    # print("Удаление данных из таблиц...")
    logger.info("Удаление данных из таблиц...")
    session.execute("""TRUNCATE TABLE photos, requests, shifts, tasks, user_tasks, users""")
    session.commit()


def generate_fake_data() -> None:
    logger.info("Генерация фейковых данных...")
    with factory.Faker.override_default_locale("ru_RU"):

        logger.info("Создание пользователей...")
        UserFactory.create_batch(FAKE_USERS_COUNT)
        logger.info(f"Создано {FAKE_USERS_COUNT} пользователей")

        logger.info("Создание заданий...")
        TaskFactory.create_batch(FAKE_TASK_COUNT)
        logger.info(f"Создано {FAKE_TASK_COUNT} заданий")

        logger.info("Создание фотографий...")
        PhotoFactory.create_batch(FAKE_PHOTO_COUNT)
        logger.info(f"Создано {FAKE_PHOTO_COUNT} фотографий")

        task_ids_list = SESSION.execute(select(Task.id))
        task_ids_list = task_ids_list.scalars().all()
        random.shuffle(task_ids_list)

        generate_started_shifts(task_ids_list)
        generate_preparing_shifts()
        generate_finished_shifts(task_ids_list)
    logger.info("Создание тестовых данных завершено!")


@click.command()
@click.option('--delete', is_flag=True, help="Удаление существующих данных из таблиц")
def fill_command(delete) -> None:
    if delete:
        truncate_tables(SESSION)
        generate_fake_data()
    else:
        try:
            generate_fake_data()
        except IntegrityError:
            logger.error("Повторное наполнение БД тестовыми данными не предусмотрено!")


if __name__ == "__main__":
    fill_command()
