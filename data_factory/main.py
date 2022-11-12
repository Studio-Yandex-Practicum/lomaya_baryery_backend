import factory
from sqlalchemy.orm import Session

from data_factory.factories import SESSION, RequestFactory, UserTaskFactory

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
        RequestFactory.create_batch(data_quantity)
        UserTaskFactory.create_batch(data_quantity)
    print("Выполнено")


if __name__ == "__main__":
    generate_fake_data()
