import logging
import sys
from uuid import UUID

import click
import factory
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from data_factory.factories import (
    MemberFactory,
    RequestFactory,
    ShiftFactory,
    TaskFactory,
    UserFactory,
    session,
)
from src.core.db.models import Member, Request, Shift, User


def get_logger(log_filename: str) -> logging.Logger:
    file_handler = logging.FileHandler(filename=f'data_factory/{log_filename}', encoding='utf-8')
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    handlers = [file_handler, stdout_handler]
    format = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
    name = 'fill_db_log'
    logging.basicConfig(level=logging.INFO, handlers=handlers, format=format)
    return logging.getLogger(name)


logger = get_logger('fill_db.log')


def get_random_user_ids(count: int, status: User.Status) -> list:
    user_ids = session.execute(select(User.id).where(User.status == status).order_by(func.random()).limit(count))
    return user_ids.scalars().all()


def truncate_tables(session: Session) -> None:
    """Очистить таблицы БД."""
    logger.info("Удаление данных из таблиц...")
    session.execute("""TRUNCATE TABLE requests, shifts, tasks, reports, users, members""")
    session.commit()


def create_approved_requests_and_members_with_user_tasks(user_ids: list[UUID], shift: Shift):
    for user_id in user_ids:
        RequestFactory.create_batch(1, user_id=user_id, shift_id=shift.id, status=Request.Status.APPROVED)

        MemberFactory.complex_create(1, user_id=user_id, shift_id=shift.id, status=Member.Status.ACTIVE)


def create_declined_requests(user_ids: list[UUID], shift: Shift):
    for user_id in user_ids:
        RequestFactory.create(user_id=user_id, shift_id=shift.id, status=Request.Status.DECLINED)


def generate_fake_data() -> None:
    shift_user_numbers = 30
    request_user_numbers = shift_user_numbers // 2
    logger.info("Генерация фейковых данных...")
    with factory.Faker.override_default_locale("ru_RU"):

        logger.info("Создание пользователей...")
        UserFactory.create_batch(200)

        logger.info("Создание заданий...")
        TaskFactory.create_batch(31)

        logger.info("Создание активной смены...")
        started_shift = ShiftFactory.create(status=Shift.Status.STARTED)

        logger.info("Создание одобренных заявок и заданий для активной смены...")
        create_approved_requests_and_members_with_user_tasks(
            get_random_user_ids(request_user_numbers, User.Status.VERIFIED), started_shift
        )

        logger.info("Создание отклоненных заявок для активной смены...")
        create_declined_requests(get_random_user_ids(request_user_numbers, User.Status.DECLINED), started_shift)

        logger.info("Создание завершенной смены...")
        finished_shifts = ShiftFactory.create_batch(5, status=Shift.Status.FINISHED)
        for finished_shift in finished_shifts:

            logger.info("Создание одобренных заявок и заданий для завершенной смены...")
            create_approved_requests_and_members_with_user_tasks(
                get_random_user_ids(request_user_numbers, User.Status.VERIFIED), finished_shift
            )

            logger.info("Создание отклоненных заявок для завершенной смены...")
            create_declined_requests(get_random_user_ids(request_user_numbers, User.Status.DECLINED), finished_shift)

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
        truncate_tables(session)
        generate_fake_data()
    else:
        try:
            generate_fake_data()
        except IntegrityError:
            logger.error("Повторное наполнение БД тестовыми данными не предусмотрено!")


if __name__ == "__main__":
    fill_command()
