from data_factory import factories

FAKE_DATA_QUANTITY = 10


def sync_main():
    msg = (
        "ВНМАНИЕ! Дальнейшее действие приведет к удалению ВСЕХ существующих данных из ВСЕХ таблиц БД!\n"
        "Продолжить?(y/n)"
    )
    if input(msg).lower().strip() not in ["y", "yes"]:
        return
    factories.RequestFactory.create_batch(FAKE_DATA_QUANTITY)
    factories.UserTaskFactory.create_batch(FAKE_DATA_QUANTITY)
