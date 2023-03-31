# Бэкенд проекта "Ломая барьеры"

<details>
  <summary>Оглавление</summary>
  <ol>
    <li>
      <a href="#описание">Описание</a>
      <ul>
        <li><a href="#технологии">Технологии</a></li>
      </ul>
    </li>
    <li>
      <a href="#установка-и-запуск">Установка и запуск</a>
      <ul>
        <li>
          <a href="#зависимости">Зависимости</a>
          <ul>
            <li><a href="#poetry">Poetry</a></li>
          </ul>
        </li>
        <li><a href="#установка">Установка</a></li>
        <li><a href="#запуск">Запуск</a></li>
      </ul>
    </li>
    <li><a href="#использование">Использование</a></li>
    <li>
      <a href="#полезная-информация">Дополнительная информация</a>
      <ul>
        <li>
          <a href="#режимы-работы-бота">Режимы работы бота</a>
          <ul>
            <li><a href="#запуск-без-api-приложения">Запуск без API приложения</a></li>
            <li><a href="#polling">Polling</a></li>
            <li><a href="#webhook">Webhook</a></li>
          </ul>
        </li>
        <li>
          <a href="#работа-с-базой-данных">Работа с базой данных</a>
          <ul>
            <li><a href="#тестовые-данные">Тестовые данные</a></li>
            <li><a href="#создание-миграций">Создание миграций</a></li>
            <li><a href="#откат-миграций">Откат миграций</a></li>
            <li><a href="#миграции-с-enum-полем">Миграции с Enum-полем</a></li>
          </ul>
        </li>
        <li>
          <a href="#работа-с-poetry">Работа с Poetry</a>
          <ul>
            <li><a href="#активировать-виртуальное-окружение">Активировать виртуальное окружение</a></li>
            <li><a href="#добавить-зависимость">Добавить зависимость</a></li>
            <li><a href="#запустить-скрипт-без-активации-виртуального-окружения">Запустить скрипт без активации виртуального окружения</a></li>
          </ul>
        </li>
        <li><a href="#использование-ngrok">Использование Ngrok</a></li>
        <li><a href="#переменные-окружения-env">Переменные окружения (.env)</a></li>
      </ul>
    </li>
  </ol>
</details>

<a name="описание"></a>

Проект включает в себя телеграм-бота и сайт администратора,
которые используются для сбора ежедневных результатов заданий,
выполненных детьми дома. Задания направлены на развитие социально-бытовых
навыков, таких как чистка зубов, стирка и мытье посуды.
По итогам трехмесячной смены "Умею жить" дети получают заслуженные награды.

В настоящее время отправка фотографий в общий чат является основным
способом отчетности, что приводит к некоторым неудобствам.
Например, большой объем фотографий необходимо анализировать вручную,
а также возможны случаи повторной отправки изображений.

Для упрощения этого процесса мы работаем над внедрением
новых инструментов отчетности, которые помогут сделать процесс более
автоматизированным и эффективным.

### Технологии

[![FastAPI][FastAPI-badge]][FastAPI-url]
[![Python-telegram-bot][Python-telegram-bot-badge]][Python-telegram-bot-url]
[![Postgres][Postgres-badge]][Postgres-url]
[![Nginx][Nginx-badge]][Nginx-url]

## Установка и Запуск

В данном разделе представлен минимальный набор инструкции,
необходимых для запуска приложения.

### Зависимости

> **Warning**:
> Необходимы для дальнейшей разработки приложения.

#### Poetry

Это инструмент управления зависимостями и виртуальным окружением,
также используется для упаковки проектов на Python.

Подробнее: https://python-poetry.org/

1. Установить, следуя официальным инструкциям.

    https://python-poetry.org/docs/#installation

2. Изменить конфигурацию Poetry (опционально).

    ```shell
    poetry config virtualenvs.in-project true
    ```
    > **Note**:
    > Позволяет создавать виртуальное окружение в папке проекта.

### Установка

1. Клонировать репозиторий.

    ```shell
    git clone https://github.com/Studio-Yandex-Practicum/lomaya_baryery_backend.git
    cd lomaya_baryery_backend
    ```

2. Создать и активировать виртуальное окружение.

    ```shell
    poetry install
    poetry shell
    ```

3. Настроить pre-commit.

    ```shell
    pre-commit install
    ```

    > **Note**:
    > Перед каждым коммитом будет запущен линтер и форматтер,
    > который автоматически отформатирует код
    > согласно принятому в команде codestyle.

4. Переименовать `.env.example` в `.env` и задать переменные окружения.

    ```dotenv
    BOT_TOKEN=<Токен аутентификации бота>
    APPLICATION_URL=https://example.com  # Необязательно, пример
    ```

    > **Warning**:
    > Если не указано значение для `APPLICATION_URL`, форма регистрации в боте
    > работать не будет.

    > **Warning**:
    > Необходимо доменное имя с установленным SSL-сертификатом.
    > Иначе обратитесь к разделу "[Использование Ngrok](#использование-ngrok)".

### Запуск

1. Выполнить запуск контейнеров docker.

    ```shell
    docker-compose -f docker-compose.local.yaml up -d
    ```

    > **Note**:
    > Будет поднята Postgres база данных, а также прокси-сервер nginx.

2. Применить миграции базы данных.

    ```shell
    alembic upgrade head
    ```

3. Запустить сервер приложения.

    ```shell
    python run.py
    ```

## Использование

После выполнения инструкций, описанных в разделе
"[Установка и Запуск](#установка-и-запуск)", вы сможете получить
доступ к админке, перейдя по адресу http://localhost.

Также по адресу http://localhost/api/docs доступна полная документация API.

## Полезная информация

Данный раздел содержит информацию, которая может быть полезна для разработчиков.
Настоятельно рекомендуем каждому прочитать его хотя бы один раз.

### Режимы работы бота

#### Запуск без API приложения

1. Выполнить скрипт запуска.

    ```shell
    python run_bot.py
    ```

    > **Warning**:
    > Возможно только в режиме [polling](#polling).

#### Polling

1. Задать значение переменной окружения (.env).

    ```dotenv
    BOT_WEBHOOK_MODE=False
    ```

#### Webhook

1. Задать значение переменным окружения (.env).

    ```dotenv
    BOT_WEBHOOK_MODE=True
    APPLICATION_URL=https://example.com  # Пример
    ```

    > **Warning**:
    > Необходимо доменное имя с установленным SSL-сертификатом.
    > Иначе обратитесь к разделу "[Использование Ngrok](#использование-ngrok)".

### Работа с базой данных

#### Тестовые данные

1. Выполнить скрипт для наполнения базы тестовыми данными.

    ```shell
    python -m data_factory.main
    ```
    > **Warning**:
    > Использование в команде флага `--delete` перезапишет все данные.
    > Подробнее: [data_factory/README.md](data_factory/README.md)

#### Создание миграций

1. Применить существующие миграции.

    ```shell
    alembic upgrade head
    ```

2. Создать новую миграцию.

    ```shell
    alembic revision --autogenerate -m "<Название миграции>"
    ```

    В название миграции указывается
    для какого поля или модели внесены изменения, например:

    * add_shift_model
    * shift_add_field_title
    * shift_remove_field_title

3. Повторить пункт 1, для применения созданной миграции.

#### Откат миграций

1. Откатить последнюю миграцию.

    ```shell
    alembic downgrade -1
    ```

#### Миграции с Enum-полем

> **Warning**:
> При использовании ENUM-классов необходимо вручную определить
> создание и удаление типа в миграции.

> **Note**:
> Далее приведены инструкции для поля "статус" с заранее
> разрешенными значениями.

1. Описать тип.

    ```python
    STATUS_ENUM_POSTGRES = postgresql.ENUM('started', 'finished', 'preparing', 'cancelled', name='shift_status', create_type=False)
    STATUS_ENUM = sa.Enum('started', 'finished', 'preparing', 'cancelled', name='shift_status')
    STATUS_ENUM.with_variant(STATUS_ENUM_POSTGRES, 'postgresql')
    ```

2. Добавить к полю.

    ```python
    sa.Column('status', STATUS_ENUM, nullable=False),
    ```

3. Прописать удаление при откате миграции.

    ```python
    STATUS_ENUM.drop(op.get_bind(), checkfirst=True)
    ```

<details>
  <summary>Полный пример миграции</summary>

```python
"""init

Revision ID: bc61d3dfbfa8
Revises:
Create Date: 2022-09-18 07:27:34.175636

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bc61d3dfbfa8'
down_revision = None
branch_labels = None
depends_on = None

STATUS_ENUM_POSTGRES = postgresql.ENUM('started', 'finished', 'preparing', 'cancelled', name='shift_status', create_type=False)
STATUS_ENUM = sa.Enum('started', 'finished', 'preparing', 'cancelled', name='shift_status')
STATUS_ENUM.with_variant(STATUS_ENUM_POSTGRES, 'postgresql')

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shift',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('status', STATUS_ENUM, nullable=False),
    sa.Column('started_at', sa.DATE(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('finished_at', sa.DATE(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('shift')
    STATUS_ENUM.drop(op.get_bind(), checkfirst=True)
    # ### end Alembic commands ###

```

</details>

Если добавили значения в choice так же прописываем:

```python
def upgrade():
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE status ADD VALUE 'REJECTED'")
```

Для отката миграции:

- Переименовываем текущий тип;
- Создаем новый (с прежними значениями);
- Приписываем новый тип для таблицы;
- Удаляем старый тип.

```python
def downgrade():
    op.execute("ALTER TYPE status RENAME TO status_old")
    op.execute("CREATE TYPE status AS ENUM('STARTED', 'ACCEPTED')")
    op.execute((
        "ALTER TABLE transactions ALTER COLUMN status TYPE status USING "
        "status::text::status"
    ))
    op.execute("DROP TYPE status_old")
```

### Работа с Poetry

В этом разделе представлены наиболее часто используемые команды.

Подробнее: https://python-poetry.org/docs/cli/

#### Активировать виртуальное окружение

```shell
poetry shell
```

#### Добавить зависимость

```shell
poetry add <package_name>
```

> **Note**:
> Использование флага `--dev (-D)` позволяет установить зависимость,
> необходимую только для разработки.
> Это полезно для разделения develop и prod зависимостей.

#### Запустить скрипт без активации виртуального окружения

```shell
poetry run <script_name>.py
```

### Использование Ngrok

Этот раздел будет полезен, если у вас нет доменного имени с
установленным SSL-сертификатом.

Ngrok — это инструмент, который позволяет создавать временный
общедоступный адрес (туннель) для вашего локального сервера,
находящимся за NAT или брандмауэром.

Подробнее: https://ngrok.com/

1. Установить, следуя официальным инструкциям.

    https://ngrok.com/download

2. Запустить туннель.

    ```shell
    ngrok http 80
    ```

3. Задать значение переменной окружения (.env).

    ```dotenv
    APPLICATION_URL=https://1234-56-78-9.eu.ngrok.io  # Пример
    ```

### Переменные окружения (.env)

```dotenv
# Переменные приложения
BOT_TOKEN=  # Токен аутентификации бота
BOT_WEBHOOK_MODE=False  # Запустить бота в режиме webhook(True) | polling(False)
APPLICATION_URL=  # Домен, на котором развернуто приложение
HEALTHCHECK_API_URL=http://127.0.0.1:8080/docs  # Эндпоинт для проверки API
DEBUG=False  # Включение(True) | Выключение(False) режима отладки
SECRET_KEY=a84167ccb889a32e12e639db236a6b98877d73d54b42e54f511856e20ccaf2ab  # Cекретный ключ для генерации jwt-токенов
ROOT_PATH=/api/  # Для корректной работы без прокси ставится пустая строка, для работы с прокси "/api/"

# Переменные базы данных
POSTGRES_DB=lomaya_baryery_db_local  # Название базы данных
POSTGRES_USER=postgres  # Логин для подключения к базе данных
POSTGRES_PASSWORD=postgres  # Пароль для подключения к базе данных
DB_HOST=localhost  # Название сервиса (контейнера)
DB_PORT=6100  # Порт для подключения к базе данных

# Настройки почты для теста писем через сервис ethereal.email
MAIL_SERVER=smtp.yandex.ru  # Адрес постового сервиса
MAIL_PORT=465  # Порт для подключения к почтовому сервису
MAIL_LOGIN=  # Логин для подключения к почтовому сервису
MAIL_PASSWORD=  # Пароль для подключения к почтовому сервису
MAIL_STARTTLS=False  # True или False, использовать ли STARTTLS
MAIL_SSL_TLS=True  # True или False, использовать ли SSL и TLS
USE_CREDENTIALS=True
VALIDATE_CERTS=True
```

<!-- MARKDOWN LINKS & BADGES -->

[FastAPI-url]: https://fastapi.tiangolo.com/
[FastAPI-badge]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi

[Python-telegram-bot-url]: https://github.com/python-telegram-bot/python-telegram-bot
[Python-telegram-bot-badge]: https://img.shields.io/badge/python--telegram--bot-2CA5E0?style=for-the-badge

[Postgres-url]: https://www.postgresql.org/
[Postgres-badge]: https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white

[Nginx-url]: https://nginx.org
[Nginx-badge]: https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white~~
