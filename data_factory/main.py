import random
from datetime import timedelta

import factory
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from data_factory.factories import (SESSION, RequestFactory,
                                    UserTaskFactory, UserFactory,
                                    ShiftFactory, PhotoFactory,TaskFactory)

from src.core.db.models import User, Task

FAKE_DATA_QUANTITY = 10


def truncate_tables(session: Session) -> None:
    """Очистить таблицы БД."""
    session.execute("""TRUNCATE TABLE photos, requests, shifts, tasks, user_tasks, users""")
    session.commit()


def generate_fake_data(session: Session = SESSION, data_quantity: int = FAKE_DATA_QUANTITY) -> None:
    """Очистить таблицы БД и наполнить их тестовыми данными."""
    msg = (
        "ВНМАНИЕ! Дальнейшее действие приведет к удалению ВСЕХ существующих данных из ВСЕХ таблиц БД!\n"
        "Продолжить? (y/n): "
    )
    if input(msg).lower().strip() not in ("y", "yes"):
        return
    print("Удаление данных из таблиц...")
    truncate_tables(session)
    print("Генерация фейковых данных...")
    with factory.Faker.override_default_locale("ru_RU"):
        UserFactory.create_batch(200)
        TaskFactory.create_batch(31)
        PhotoFactory.create_batch(10)

        task_ids_list = SESSION.execute(select(Task.id))
        task_ids_list = task_ids_list.scalars().all()
        random.shuffle(task_ids_list)

        started_shifts = ShiftFactory.create_batch(1, status='started')
        for started_shift in started_shifts:
            user_ids = SESSION.execute(select(User.id).order_by(func.random()).limit(30))
            user_ids = user_ids.scalars().all()
            for user_id in user_ids[:2]:
                RequestFactory.create_batch(1, status='repeated request', user_id=user_id)
            for user_id in user_ids[2:4]:
                RequestFactory.create_batch(1, status='declined', user_id=user_id)
            for user_id in user_ids[4:]:
                RequestFactory.create_batch(1, status='approved', user_id=user_id)
                number_days = (started_shift.finished_at - started_shift.started_at).days
                all_dates = tuple((started_shift.created_at + timedelta(day)) for day in range(number_days))
                for one_date in all_dates[:2]:
                    UserTaskFactory.create_batch(
                        2,
                        task_id=task_ids_list[one_date.day - 1],
                        user_id=user_id,
                        shift_id=started_shift.id,
                        task_date=one_date,
                        status=User.Status.APPROVED
                    )
                for one_date in all_dates[2]:
                    UserTaskFactory.create(
                        task_id=task_ids_list[one_date.day - 1],
                        user_id=user_id,
                        shift_id=started_shift.id,
                        task_date=one_date,
                        status=User.Status.UNDER_REVIEW
                    )
                for one_date in all_dates[3:]:
                    UserTaskFactory.create(
                        task_id=task_ids_list[one_date.day - 1],
                        user_id=user_id,
                        shift_id=started_shift.id,
                        task_date=one_date,
                        status=User.Status.NEW
                    )

        finished_shifts = ShiftFactory.create_batch(5, status='finished')
        for finished_shift in finished_shifts:
            user_ids = SESSION.execute(select(User.id).order_by(func.random()).limit(30))
            user_ids = user_ids.scalars().all()
            for user_id in user_ids[:2]:
                RequestFactory.create_batch(1, status='repeated request', user_id=user_id)
            for user_id in user_ids[2:4]:
                RequestFactory.create_batch(1, status='declined', user_id=user_id)
            for user_id in user_ids[4:]:
                RequestFactory.create_batch(1, status='approved', user_id=user_id)
                number_days = (finished_shift.finished_at - finished_shift.started_at).days
                all_dates = tuple((finished_shift.created_at + timedelta(day)) for day in range(number_days))
                task_ids_list = SESSION.execute(select(Task.id))
                task_ids_list = task_ids_list.scalars().all()
                random.shuffle(task_ids_list)
                for one_date in all_dates[:2]:
                    print(one_date.day)
                    print(task_ids_list[one_date.day - 1])
                    UserTaskFactory.create_batch(2, task_id=task_ids_list[one_date.day - 1], status="declined")
                for one_date in all_dates[2:]:
                    UserTaskFactory.create_batch(2, task_id=task_ids_list[one_date.day - 1], status="approved")

    print("Выполнено")


import click

@click.command()
@click.option('--shout/--no-shout', default=False)
def info(shout):
    if shout:
        truncate_tables(SESSION)
        generate_fake_data(SESSION, FAKE_DATA_QUANTITY)
    else:
        click.echo('Отмена')


if __name__ == "__main__":
    info()
