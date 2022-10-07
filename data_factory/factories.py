import factory
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from src.core.db import models
from src.core.settings import settings

engine = create_engine(settings.database_url.replace("+asyncpg", "+psycopg2"))
SESSION = scoped_session(sessionmaker(bind=engine))


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.User
        sqlalchemy_session = SESSION
        sqlalchemy_session_persistence = "commit"

    id = factory.Faker("uuid4")
    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    date_of_birth = factory.Faker("date_object")
    # FIXME: испльзовать фейкер
    city = factory.Iterator(["Москва", "Санкт-Петербург", "Казань", "Нижний Новгород", "Екатеринбург", "Хабаровск"])
    phone_number = factory.Sequence(lambda n: str(89991234567 + n))
    telegram_id = factory.Sequence(lambda n: 123556789 + n)


class ShiftFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Shift
        sqlalchemy_session = SESSION
        sqlalchemy_session_persistence = "commit"

    id = factory.Faker("uuid4")
    status = factory.Iterator([status for status in models.Shift.Status])
    started_at = factory.Faker("date_object")
    finished_at = factory.Faker(
        "date_between_dates",
        date_start=factory.SelfAttribute("..started_at"),
    )


class PhotoFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Photo
        sqlalchemy_session = SESSION
        sqlalchemy_session_persistence = "commit"

    url = factory.Sequence(lambda n: f"photos/some_photo_{n}.png")


class TaskFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Task
        sqlalchemy_session = SESSION
        sqlalchemy_session_persistence = "commit"

    url = factory.Sequence(lambda n: f"tasks/{n}")
    description = factory.Faker("paragraph", nb_sentences=2)


class RequestFactory(factory.alchemy.SQLAlchemyModelFactory):
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


class UserTaskFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.UserTask
        sqlalchemy_session = SESSION
        sqlalchemy_session_persistence = "commit"

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
