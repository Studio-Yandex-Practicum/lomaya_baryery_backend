import datetime
from datetime import timedelta
import random

import factory
from sqlalchemy import create_engine, select
from sqlalchemy.orm import scoped_session, sessionmaker

from src.core.db import models
from src.core.db.models import User, Shift, Photo
from src.core.settings import settings

engine = create_engine(settings.database_url.replace("+asyncpg", "+psycopg2"))
SESSION = scoped_session(sessionmaker(bind=engine))

def get_random_objects_by_queryset(queryset, number=None):
    items = list(queryset)
    length = len(items)
    if length == 0:
        return None
    if number is not None:
        if number > length:
            number = length
        return random.sample(items, number)
    return random.choice(items)

def get_random_objects_id_by_model(model, attr_value=None, number=None):
    if attr_value:
        obj_ids = SESSION.execute(select(model.id).where(model.status == attr_value))
    else:
        obj_ids = SESSION.execute(select(model.id))
    obj_ids = obj_ids.scalars().all()
    return get_random_objects_by_queryset(obj_ids, number)

class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = SESSION
        sqlalchemy_session_persistence = "commit"


class RequestFactory(BaseFactory):
    class Meta:
        model = models.Request

    status = factory.Iterator([status for status in models.Request.Status])
    numbers_lombaryers = factory.Faker("random_int", min=0, max=92)



    @factory.lazy_attribute
    def user_id(self):
        return get_random_objects_id_by_model(User)

    @factory.lazy_attribute
    def shift_id(self):
        return get_random_objects_id_by_model(Shift)


class UserTaskFactory(BaseFactory):
    class Meta:
        model = models.UserTask

    status = factory.Iterator([status for status in models.UserTask.Status])

    @factory.lazy_attribute
    def photo_id(self):
        return get_random_objects_id_by_model(Photo)


class UserFactory(BaseFactory):
    class Meta:
        model = models.User

    id = factory.Faker("uuid4")
    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    date_of_birth = factory.Faker(
        "date_between_dates", date_start=datetime.date(2010, 1, 1), date_end=datetime.date(2030, 1, 1)
    )
    city = factory.Iterator(["Москва", "Санкт-Петербург", "Казань", "Нижний Новгород", "Екатеринбург", "Хабаровск"])
    phone_number = factory.Sequence(lambda n: str(8999123456 + n))
    telegram_id = factory.Sequence(lambda n: 12355678 + n)
    numbers_lombaryers = factory.Faker("random_int", min=0, max=92)


class ShiftFactory(BaseFactory):
    class Meta:
        model = models.Shift

    id = factory.Faker("uuid4")
    status = factory.Iterator([status for status in models.Shift.Status])
    title = factory.Faker("text", max_nb_chars=25)
    final_message = factory.Faker("text", max_nb_chars=25)

    @factory.lazy_attribute
    def started_at(self):
        if self.status == "started":
            started_at = datetime.date.today() - timedelta(days=2)
            return started_at
        if self.status == "finished":
            last_started_shift = SESSION.execute(select(Shift).order_by(Shift.started_at))
            last_started_shift = last_started_shift.scalars().first()
            started_at = last_started_shift.started_at - timedelta(days=random.randrange(4, 7)) - timedelta(days=90)
            return started_at

    @factory.lazy_attribute
    def finished_at(self):
        finished_at = self.started_at + timedelta(days=random.randrange(90,93))
        return finished_at


class PhotoFactory(BaseFactory):
    class Meta:
        model = models.Photo

    url = factory.Sequence(lambda n: f"photos/some_photo_{n}.png")


class TaskFactory(BaseFactory):
    class Meta:
        model = models.Task

    url = factory.Sequence(lambda n: f"tasks/{n}")
    description = factory.Faker("paragraph", nb_sentences=2)
