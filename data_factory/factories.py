import factory
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from src.core.db import models
from src.core.settings import settings

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
    date_of_birth = factory.Faker("date_object")
    city = factory.Iterator(["Москва", "Санкт-Петербург", "Казань", "Нижний Новгород", "Екатеринбург", "Хабаровск"])
    phone_number = factory.Sequence(lambda n: str(89991234567 + n))
    telegram_id = factory.Sequence(lambda n: 123556789 + n)


class ShiftFactory(BaseFactory):
    class Meta:
        model = models.Shift

    id = factory.Faker("uuid4")
    status = factory.Iterator([status for status in models.Shift.Status])
    started_at = factory.Faker("date_object")
    finished_at = factory.Faker(
        "date_between_dates",
        date_start=factory.SelfAttribute("..started_at"),
    )


class PhotoFactory(BaseFactory):
    class Meta:
        model = models.Photo

    url = factory.Sequence(lambda n: f"photos/some_photo_{n}.png")


class TaskFactory(BaseFactory):
    class Meta:
        model = models.Task

    url = factory.Sequence(lambda n: f"tasks/{n}")
    description = factory.Faker("paragraph", nb_sentences=2)


class RequestFactory(BaseFactory):
    class Meta:
        model = models.Request
        sqlalchemy_session = SESSION
        sqlalchemy_session_persistence = "commit"

    class Params:
        shift = factory.SubFactory(ShiftFactory)
        user = factory.SubFactory(UserFactory)

    shift_id = factory.SelfAttribute("shift.id")
    user_id = factory.SelfAttribute("user.id")
    status = factory.Iterator([status for status in models.Request.Status])


class UserTaskFactory(BaseFactory):
    class Meta:
        model = models.UserTask

    class Params:
        user = factory.SubFactory(UserFactory)
        shift = factory.SubFactory(ShiftFactory)
        task = factory.SubFactory(TaskFactory)
        photo = factory.SubFactory(PhotoFactory)

    user_id = factory.SelfAttribute("user.id")
    shift_id = factory.SelfAttribute("shift.id")
    task_id = factory.SelfAttribute("task.id")
    day_number = factory.Faker("random_int", min=1, max=99)
    status = factory.Iterator([status for status in models.UserTask.Status])
    photo_id = factory.SelfAttribute("photo.id")
