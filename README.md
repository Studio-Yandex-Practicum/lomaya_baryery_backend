# lomaya_baryery_backend

## Настройка poetry <a id="poetry"></a>:

Poetry - это инструмент для управления зависимостями и виртуальными
окружениями,
также может использоваться для сборки пакетов.

### Установка:

Для UNIX систем вводим в консоль следующую команду

> *curl -sSL https://install.python-poetry.org | python3 -*

Для WINDOWS вводим в PowerShell

> *(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -*

После установки перезапустите оболочку и введите команду

> poetry --version

Ответ должен быть в формате

> Poetry version 1.1.13

В случае, если вы видите ошибку "команда не найдена", проверьте, что в PATH внесён путь
(вместо USERNAME должно быть имя пользователя):
> C:\Users\USERNAME\AppData\Roaming\Python\Scripts (для Windows)
>
> /Users/USERNAME/Library/Application Support/pypoetry/venv/bin (для Mac)

Здесь вы можете ознакомиться подробнее с процессом установки Poetry:
> https://python-poetry.org/docs/#installation

Для дальнейшей работы введите команду:

> poetry config virtualenvs.in-project true

Выполнение данной команды необходимо для создания виртуального окружения в
папке проекта,
по умолчанию папка .venv создается по пути **C:\Users\<username>
\AppData\Local\pypoetry\Cache\virtualenvs**

После предыдущей команды создадим виртуальное окружение нашего проекта с
помощью команды

> poetry install

Результатом выполнения команды станет создание в корне проекта папки .venv.
Зависимости для создания окружения берутся из файлов poetry.lock (приоритетнее)
и pyproject.toml

Для добавления новой зависимости в окружение необходимо выполнить команду

> poetry add <package_name>
>
> poetry add starlette *пример использования*

Также poetry позволяет разделять зависимости необходимые для разработки, от
основных.
Для добавления зависимости необходимой для разработки и тестирования необходимо
добавить флаг ***--dev***

> poetry add <package_name> --dev
>
> poetry add pytest --dev *пример использования*

### Порядок работы после настройки

Чтобы активировать виртуальное окружение введите команду:

> poetry shell

Существует возможность запуска скриптов и команд с помощью команды без
активации окружения:

> poetry run <script_name>.py
>

или

> poetry run python script_name>.py
>
> poetry run pytest
>
> poetry run black

Порядок работы в оболочке не меняется. Пример команды для Win:

> C:\Dev\nenaprasno_bot\ask_nenaprasno_bot>python src\run_bot.py

Доступен стандартный метод работы с активацией окружения в терминале с помощью
команд:

Для WINDOWS:

> source .venv/Scripts/activate

Для UNIX:

> source .venv/bin/activate

## Настройка pre-commit <a id="pre-commit"></a>:

> poetry install
>
> pre-commit install

Далее при каждом коммите у вас будет происходить автоматическая проверка
линтером, а так же будет происходить автоматическое приведение к единому стилю.

Если у вас произошло появление сообщений об ошибках, то в большинстве случаев
достаточно повторить добавление файлов вызвавших ошибки в git и повторный
коммит:

> git add .
>
> git commit -m "Текст комментария коммита"

## Переменные окружения:

```dotenv
POSTGRES_DB=lomaya_baryery_db_local  # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД
DB_HOST=0.0.0.0 # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
BOT_TOKEN=
```

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


### Запуск одного бота:

```shell
python run_bot.py
```

## Запустить проект локально:

```shell
python run.py
```

## Запуск docker-compose:

```shell
docker-compose up
```

### Проект доступен

```
http://127.0.0.1:8080
http://0.0.0.0:8080
http://localhost:8080
```

## endpoins:

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