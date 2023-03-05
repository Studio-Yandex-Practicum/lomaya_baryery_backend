# Бэкенд проекта "Ломая барьеры"<br /><br />1. О чём проект?

#### Проект состоит из телеграм-бота, сайта админки, куда дети или их родители присылают ежедневно результаты неких действий. Дети выполняют дома задания, направленные на формирование социально-бытовых навыков (почистить зубы, постирать, помыть посуду), отчитываются по ним, а потом по итогам трехмесячной смены “Умею жить” получают награды.<br />
#### Сейчас это реализовано направлением фотографий в общий чат, что вызывает некоторые неудобства из-за большого объема, который необходимо самостоятельно проанализировать, иногда фотографии могут отправляться повторно.

# 2. Начало работы

## 2.1. Poetry (инструмент для работы с виртуальным окружением и сборки пакетов) <a id="poetry"></a>:

Poetry - это инструмент для управления зависимостями и виртуальными окружениями, также может использоваться для сборки пакетов. В этом проекте Poetry необходим для дальнейшей разработки приложения.

<details>
 <summary>
 Как скачать и установить?
 </summary>

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

</details>

<details>
 <summary>
 Порядок работы после настройки
 </summary>

<br />

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

</details>

<details>
 <summary>
 Настройка pre-commit <a id="pre-commit"></a>
 </summary>
<br />
> poetry install
>
> pre-commit install

Далее при каждом коммите у вас будет происходить автоматическая проверка
линтером, а так же будет происходить автоматическое приведение к единому стилю.
</details>

# 3. БД

## 3.1. Запуск локальной БД

<details>
 <summary>
 Запуск
 </summary>
<br />

```shell
docker-compose -f docker-compose.local.yaml up
```
Если у вас запущен Postgres на компьютере, то остановите его или создайте базу для проекта там.

</details>

## 3.2. Миграции

<details>
 <summary>
 При первом запуске необходимо применить существующие миграции, чтобы в БД создались таблицы
 </summary>
<br />

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
</details>

### 3.2.1. Откат миграций

<details>
 <summary>
 Чтобы откатить последнюю миграции, используйте
 </summary>
<br />

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

</details>

## 3.3. Тестовые данные БД

<details>
 <summary>
 Подробнее
 </summary><br>

В проекте реализована возможность генерации фейковых (тестовых) данных для БД.<br />

Команда для наполнения БД данными

```shell
py -m data_factory.main
```
#### !!! Внимание!!!
Использование в указанной команде флага `--delete`приведет к удалению
существующих в таблицах данных! База данных повторно заполнится тестовыми данными.

Процесс наполнения БД тестовыми данными подробно описан в `data_factory/README.md`

</details>

# 4. Работа с ботом

## 4.1. Запуск проекта локально

<details>
 <summary>
 Запуск проекта локально
 </summary>
<br />

```shell
python run.py
```

Обратите внимание, что без указания доменного имени с установленным  SSL-сертификатом для переменной **APPLICATION_URL** в переменных окружения, форма регистрации бота загружаться **не будет**. Чтобы этого избежать при локальном тестировании, воспользуйтесь инструкцией, указанной в пункте [4.2.2.1](#4221-отладка-приложения-с-ботом-в-режиме-webhook-на-локальном-компьютере)

</details>

## 4.2. Выбор режима работы бота.
### Возможен запуск бота в режимах `polling` или `webhook`.<br/>

### 4.2.1. Polling

<details>
 <summary>
 Запуск
 </summary><br />

Для запуска бота в режиме `polling` нужно установить переменной окружения `BOT_WEBHOOK_MODE` значение `false`. Дополнительных настроек не требуется.

</details>

#### 4.2.1.1. Запуск одного бота без апи только в режиме `polling`

<details>
 <summary>
 Запуск
 </summary><br>

Бот без апи запускается только в режиме `polling`.
```shell
python run_bot.py
```
</details>

### 4.2.2. Webhook

<details>
 <summary>
 Запуск
 </summary><br />

Для запуска бота в режиме `webhook` нужно установить переменной окружения `BOT_WEBHOOK_MODE` значение `true`, а также указать домен, на котором развернуто приложение в переменной `APPLICATION_URL`:

```
BOT_WEBHOOK_MODE=true
APPLICATION_URL=https://example.ngrok.io
```

</details>

#### 4.2.2.1. Отладка приложения с ботом в режиме webhook на локальном компьютере

<details>
 <summary>
 Необходимые действия
 </summary><br>

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
</details>

## 4.3 Переменные окружения

<details>
 <summary>
 Переменные окружения
 </summary>
<br />

```dotenv
POSTGRES_DB=lomaya_baryery_db_local  # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД
DB_HOST=localhost # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
BOT_TOKEN= # токен бота
BOT_WEBHOOK_MODE=False # запустить бота в режиме webhook(true)|polling(false)
APPLICATION_URL= # домен, на котором развернуто приложение
SEND_NEW_TASK_HOUR=8  # время отправки нового задания
SEND_NO_REPORT_REMINDER_HOUR=20  # время отправки напоминания об отчёте
HEALTHCHECK_API_URL=http://127.0.0.1:8080/docs # эндпоинт для проверки API

```
Перед запуском проекта необходимо создать копию файла
```.env.example```, назвав его ```.env``` и установить значения:
 - `BOT_TOKEN` - токен бота;
 - `APPLICATION_URL` - домен, на котором развернуто приложение;

</details>
