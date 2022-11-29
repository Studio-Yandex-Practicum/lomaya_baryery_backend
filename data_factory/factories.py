import datetime
from datetime import timedelta
import random

import factory
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import scoped_session, sessionmaker

from src.core.db import models
from src.core.db.models import Shift, UserTask, Task, Photo
from src.core.settings import settings

STARTED_SHIFT_DURATION = 30
MAX_USER_BIRTH_DATE = datetime.date(1986, 1, 1)
MIN_USER_BIRTH_DATE = datetime.date(2016, 1, 1)

engine = create_engine(settings.database_url.replace("+asyncpg", "+psycopg2"))
SESSION = scoped_session(sessionmaker(bind=engine))


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = SESSION
        sqlalchemy_session_persistence = "commit"


class UserFactory(BaseFactory):
    class Meta:
        model = models.User

    id = factory.Faker("uuid4")
    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    date_of_birth = factory.Faker(
        "date_between_dates", date_start=MAX_USER_BIRTH_DATE, date_end=MIN_USER_BIRTH_DATE
    )
    city = factory.Iterator(["Москва", "Санкт-Петербург", "Казань", "Нижний Новгород", "Екатеринбург", "Хабаровск"])
    phone_number = factory.Sequence(lambda n: str(89991234567 + n))
    telegram_id = factory.Sequence(lambda n: 123556787 + n)
    numbers_lombaryers = factory.Faker("random_int", min=0, max=92)


class ShiftFactory(BaseFactory):
    class Meta:
        model = models.Shift

    id = factory.Faker("uuid4")
    status = factory.Iterator([status for status in models.Shift.Status])
    title = factory.Faker("text", max_nb_chars=25)
    final_message = factory.Faker("text", max_nb_chars=80)

    @factory.lazy_attribute
    def started_at(self):
        if self.status == Shift.Status.STARTED:
            started_at = datetime.date.today() - timedelta(days=STARTED_SHIFT_DURATION)
            return started_at
        if self.status == Shift.Status.FINISHED:
            last_started_shift = SESSION.execute(select(Shift).order_by(Shift.started_at))
            last_started_shift = last_started_shift.scalars().first()
            started_at = last_started_shift.started_at - timedelta(days=random.randrange(4, 7)) - timedelta(days=90)
            return started_at
        if self.status == Shift.Status.PREPARING:
            finished_date_started_shift = SESSION.execute(
                (select(Shift.finished_at).where(Shift.status == Shift.Status.STARTED))
            )
            finished_date_started_shift = finished_date_started_shift.scalars().first()
            started_at = finished_date_started_shift + timedelta(days=random.randrange(4, 7))
            return started_at

    @factory.lazy_attribute
    def finished_at(self):
        finished_at = self.started_at + timedelta(days=90)
        return finished_at


class TaskFactory(BaseFactory):
    class Meta:
        model = models.Task

    url = factory.Sequence(lambda n: f"tasks/{n}")
    description = factory.Faker("paragraph", nb_sentences=2)


class RequestFactory(BaseFactory):
    class Meta:
        model = models.Request

    id = factory.Faker("uuid4")
    status = factory.Iterator([status for status in models.Request.Status])
    numbers_lombaryers = factory.Faker("random_int", min=0, max=92)

    @factory.post_generation
    def add_several_user_tasks(self, created, count, **kwargs):
        start_date = SESSION.execute(select(Shift.started_at).where(Shift.id == self.shift_id))
        start_date = start_date.scalars().first()
        all_dates = list((start_date + timedelta(day)) for day in range(91))
        for date in all_dates:
            if created and count:
                UserTaskFactory.create_batch(
                    count,
                    user_id=self.user_id,
                    shift_id=self.shift_id,
                    task_date=date,
                )

    @classmethod
    def complex_create(cls, count, **kwargs):
        return cls.create_batch(
            count,
            add_several_user_tasks=1,
            **kwargs,
        )


class UserTaskFactory(BaseFactory):
    class Meta:
        model = models.UserTask

    @factory.lazy_attribute
    def status(self):
        if self.task_date < datetime.date.today():
            return UserTask.Status.APPROVED
        if self.task_date == datetime.date.today():
            return UserTask.Status.UNDER_REVIEW
        else:
            return UserTask.Status.NEW

    @factory.lazy_attribute
    def task_id(self):
        task_ids = SESSION.execute(
            select(Task.id).order_by(func.random()))
        return task_ids.scalars().first()

    @factory.lazy_attribute
    def photo_id(self):
        photo_ids = SESSION.execute(
            select(Photo.id).order_by(func.random()))
        return photo_ids.scalars().first()
