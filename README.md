# lomaya_baryery_backend
# Бэкенд проекта "Ломая барьеры"

## Настройка poetry <a id="poetry"></a>:

Poetry - это инструмент для управления зависимостями и виртуальными
окружениями,
также может использоваться для сборки пакетов.

В этом проекте Poetry необходим для дальнейшей разработки приложения.

### Установка:

Установите poetry следуя [инструкции с официального сайта](https://python-poetry.org/docs/#installation).

После установки перезапустите оболочку и введите команду

> poetry --version

Если установка прошла успешно, вы получите ответ в формате

> Poetry version 1.1.13


Для дальнейшей работы введите команду:

> poetry config virtualenvs.in-project true

Выполнение данной команды необходимо для создания виртуального окружения в
папке проекта.

После предыдущей команды создадим виртуальное окружение нашего проекта с
помощью команды

> poetry install

Результатом выполнения команды станет создание в корне проекта папки .venv.
Зависимости для создания окружения берутся из файлов poetry.lock (приоритетнее)
и pyproject.toml

Для добавления новой зависимости в окружение необходимо выполнить команду

> poetry add <package_name>

_Пример использования:_

> poetry add starlette

Также poetry позволяет разделять зависимости необходимые для разработки, от
основных.
Для добавления зависимости необходимой для разработки и тестирования необходимо
добавить флаг ***--dev***

> poetry add <package_name> --dev

_Пример использования:_

> poetry add pytest --dev


### Порядок работы после настройки

Чтобы активировать виртуальное окружение введите команду:

> poetry shell

Существует возможность запуска скриптов и команд с помощью команды без
активации окружения:

> poetry run <script_name>.py


_Примеры:_

> poetry run python script_name>.py
>
> poetry run pytest
>
> poetry run black

Порядок работы в оболочке не меняется. Пример команды для Win:

> python src\run_bot.py


## Настройка pre-commit <a id="pre-commit"></a>:

> poetry install
>
> pre-commit install

Далее при каждом коммите у вас будет происходить автоматическая проверка
линтером, а так же будет происходить автоматическое приведение к единому стилю.


## Переменные окружения:

```dotenv
BOT_TOKEN= # токен бота
BOT_WEBHOOK_MODE= # запустить бота в режиме webhook(true)|polling(false)
APPLICATION_URL= # домен, на котором развернуто приложение
POSTGRES_DB=lomaya_baryery_db_local  # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД
DB_HOST=localhost # адрес БД
DB_PORT=5432 # порт для подключения к БД

```
Перед запуском проекта необходимо создать копию файла
```.env.example```, назвав его ```.env``` и установить значение токена бота

## Запустить локальную БД через docker-compose:
```shell
docker-compose -f docker-compose.local.yaml up
```
Если у вас запущен Postgres на компьютере, то остановите его или создайте базу для проекта там.

## Миграции:
При первом запуске необходимо применить существующие миграции, чтобы в БД создались таблицы:

```shell
alembic upgrade head
```

После изменения модели или добавления новой модели, необходимо создать миграцию:
```shell
alembic revision --autogenerate -m "<Название миграции>"
```
В Названии миграции указать какую модель или поле в модели добавили или удалили.

Например
- add_shift_model
- shift_add_field_title
- shift_remove_field_title

После создания миграции ее необходимо применить:
```shell
alembic upgrade head
```

Чтобы откатить последнюю миграции, используйте:
```shell
alembic downgrade -1
```

Если используются ENUM классы, например поле статус с заранее разрешенными значениями
нужно вручную прописать в миграции создание и удаление типа

Описываем тип
```python
STATUS_ENUM_POSTGRES = postgresql.ENUM('started', 'finished', 'preparing', 'cancelled', name='shift_status', create_type=False)
STATUS_ENUM = sa.Enum('started', 'finished', 'preparing', 'cancelled', name='shift_status')
STATUS_ENUM.with_variant(STATUS_ENUM_POSTGRES, 'postgresql')
```
добавляем к полю
```python
sa.Column('status', STATUS_ENUM, nullable=False),
```
Прописываем удаление при откате миграции
```python
STATUS_ENUM.drop(op.get_bind(), checkfirst=True)
```
Пример из миграции
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

Если добавили значения в choice так же прописываем

```python
def upgrade():
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE status ADD VALUE 'REJECTED'")
```
Для отката миграции
- переименовываем текущий тип
- создаем новый (с прежними значениями)
- приписываем новый тип для таблицы
- удаляем старый тип

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

## Запуск проекта локально:

```shell
python run.py
```

## Выбор режима работы бота
Возможен запуск бота в режимах `polling` или `webhook`.<br/>

### Polling
Для запуска бота в режиме `polling` нужно установить переменной окружения `BOT_WEBHOOK_MODE` значение `false`. Дополнительных настроек не требуется.

### Webhook
Для запуска бота в режиме `webhook` нужно установить переменной окружения `BOT_WEBHOOK_MODE` значение `true`, а также указать домен, на котором развернуто приложение в переменной `APPLICATION_URL`:
```
BOT_WEBHOOK_MODE=true
APPLICATION_URL=https://example.com
```

### Запуск одного бота:
Бот без апи запускается только в режиме `polling`.
```shell
python run_bot.py
```

## Отладка приложения с ботом в режиме webhook на локальном компьютере
В случае отсутствия сервера с доменным именем и установленным SSL-сертификатом, для отладки приложения можно воспользоваться <a href="https://ngrok.com/">ngrok</a> для построения туннеля до вашего компьютера.<br>
Для этого необходимо:
 - Скачать и установить <a href="https://ngrok.com/">ngrok</a>
 - Зарегестрироваться в сервисе <a href="https://ngrok.com/">ngrok</a> и получить <a href="https://dashboard.ngrok.com/get-started/your-authtoken">токен</a>
 - зарегистрировать полученный токен на локальном комьютере
 ```shell
 ngrok config add-authtoken <ваш токен>
 ```
 - Запустить тоннель ngrok
 ```shell
 ngrok http 8080
 ```
 - в переменной окружения `APPLICATION_URL` указать адрес (`https`), предоставленный сервисом `ngrok`:
 ```dotenv
 APPLICATION_URL=https://1234-56-78-9.eu.ngrok.io # пример
 ```
 - Запустить приложение с ботом в режиме webhook (см. выше)
  ```shell
 python run.py
 ```

Более подробная информация об использовании сервиса ngrok доступна на <a href="https://ngrok.com/">официальном сайте</a>


## Запуск docker-compose:

```shell
docker-compose up
```

### Проект доступен по следующим адресам:

```
http://127.0.0.1:8080
http://0.0.0.0:8080
http://localhost:8080
```

## API endpoints:

- **GET**```/hello```: Получить сообщение "hello world!"

### response

```json
{
  "answer": "hello world!"
}
```

## Comands for Bot:

- ```/start```: Запустить бота и получить приветственное сообщение

```text
Это бот Центра "Ломая барьеры", который в игровой форме поможет
особенному ребенку стать немного самостоятельнее!
Выполняя задания каждый день, ребенку будут начислять виртуальные
"ломбарьерчики". Каждый месяц мы будем подводить итоги и
награждать самых активных и старательных ребят!
```

## Тестовые данные БД
В проекте реализована возможность генерации фейковых (тестовых) данных для БД.<br />
Для наполнения таблиц таблиц необходимо:
 - установить необходмиые зависимости
  ```shell
 poetry install
 ```
 - наполнить БД тестовыми данными **Внимание! Перед генерацией тестовых данных, произойдет полное удаление существующих данных БД!**
  ```shell
 python generate_fake_data.py
 ```
