# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Бэкенд проекта «Ломая барьеры»: FastAPI-приложение с админским API плюс боты двух мессенджеров.
Дети выполняют ежедневные бытовые задания и присылают фотоотчёты, администраторы проверяют их
через API. Комментарии, докстринги и сообщения пользователям — на русском; придерживайтесь этого.

## Окружение

**Проект работает только на Python 3.10** — это не предпочтение, а жёсткое ограничение lock-файла:
пины начала 2023 года не собираются под новыми интерпретаторами (`asyncpg 0.24.0` падает под 3.11 и
выше, `multidict 6.0.4` — под 3.12 и выше). Требуемые версии заданы `Dockerfile` и продублированы
в README как обязательные: Python 3.10 (`python:3.10-slim-buster`) и **Poetry 1.3.2**;
установка — `poetry install --without dev`.

Если единственный `python3` в PATH новее 3.10, poetry возьмёт его по умолчанию и установка упадёт на
сборке C-расширений — интерпретатор надо задавать явно через `poetry env use`.

`--without dev` отключает `factory-boy`, `psycopg2-binary` и `pre-commit`, то есть недоступны
`data_factory` и pre-commit-хуки; миграции и запуск приложения от dev-группы не зависят.

`poetry.lock` имеет `lock-version = "2.0"` и читается poetry 1.3.x. Не перегенерируйте его poetry 2.x —
новый формат старая версия не прочтёт. В poetry 2.x также нет `poetry shell` и требуется `--no-root`
(пакета `lomaya_baryery_backend` в репозитории нет, код лежит в `src/`).

## Частые команды

```shell
docker-compose -f docker-compose.local.yaml up -d  # Postgres на порту 6100, nginx на 80, сборка фронта
alembic upgrade head
python run.py       # API + оба бота, uvicorn на 0.0.0.0:8080; наружу проксирует nginx (http://localhost)
python run_bot.py   # только боты, без API; возможно лишь в режиме polling
python -m data_factory.main  # тестовые данные (нужна dev-группа)
```

Линтеры (ровно то, что гоняет CI в `.github/workflows/codestyle.yml`):

```shell
python -m flake8
black . --diff
```

Форматирование: `black . --line-length 120 --skip-string-normalization`, isort — `--settings setup.cfg`.
Длина строки 120, `max-complexity = 10`, правила докстрингов D100–D107 отключены.

Миграции: `alembic revision --autogenerate -m "<название>"`, откат `alembic downgrade -1`. Без БД
миграции проверяются офлайн: `alembic upgrade <from>:<to> --sql`. CI дополнительно сверяет модели с
миграциями через `alembic-autogen-check --config ./alembic.ini` — расхождение ломает сборку.

**Тестов в репозитории нет.** CI ограничивается линтерами, проверкой миграций и healthcheck'ом
задеплоенного приложения. Не выдумывайте команды запуска тестов и не ссылайтесь на несуществующий сьют.

## Архитектура

Слои: обработчик (HTTP-роутер или хендлер бота) → сервис (`src/core/services/`) →
репозиторий (`src/core/db/repository/`) → асинхронные модели SQLAlchemy (`src/core/db/models.py`).
Обработчики не обращаются к репозиториям напрямую, репозитории не знают о бизнес-правилах.

**Точка сборки** — `create_app()` в [src/application.py](src/application.py): регистрирует роутеры и
обработчики исключений, а на событии `startup` поднимает **оба бота** и складывает их в `app.state`.
То есть `python run.py` — это API вместе с ботами, а не только API.

**API.** Роутеры используют классы-представления `fastapi_restful.cbv`: сервисы объявляются
атрибутами класса через `Depends()`, токен — через `Depends(HTTPBearer())`. Авторизация не
middleware, а явный вызов `AuthenticationService.check_administrator_by_token(self.token)` в начале
каждого защищённого эндпоинта — при добавлении эндпоинта его легко забыть.

**Ошибки.** Иерархия в `src/core/exceptions.py` наследуется от `ApplicationError`; репозитории и
сервисы бросают домен-специфичные исключения (`ObjectNotFoundError`, `ExceededAttemptsReportError`
и т.п.), а `src/core/exception_handlers.py` превращает их в HTTP-ответы. Не возвращайте `None` из
слоя данных там, где ожидается сущность: `AbstractRepository.get` уже бросает нужную ошибку.

**Два пути внедрения зависимостей — ключевая особенность.** Сервисы принимают репозитории через
`Depends()` в `__init__`, что работает только внутри HTTP-запроса. Вне запроса (хендлеры ботов,
джобы планировщика) те же сервисы собираются руками из генератора сессий фабриками в
[src/bot/api_services.py](src/bot/api_services.py). Меняя конструктор сервиса, поправьте и
соответствующую фабрику — иначе сломается бот, а не API, и линтеры этого не заметят.

**Два мессенджера.** `src/bot/` — telegram (python-telegram-bot), основной канал; `src/max_bot/` —
Max (библиотека `aiomax`), дополнительный. Общее лежит в `src/bots/`: контракт `MessageSender`,
декораторы `check_user_blocked` и `retry`, единый `error_handler`, помечающий пользователя
заблокированным. Исходящие уведомления идут через `BotService` в
[src/bots/bot_service.py](src/bots/bot_service.py), который маршрутизирует по пользователю: при
заполненном `user.max_user_id` — в Max, иначе в telegram.

Соглашение об именах: telegram-сущности носят «голые» имена (`BOT_TOKEN`, `telegram_id`,
`start_bot`), Max-сущности всегда с префиксом `max_`. Max необязателен — при пустом `MAX_BOT_TOKEN`
он просто не запускается.

Два обхода циклических импортов, которые надо сохранять: синглтон Max-бота живёт в листовом модуле
`src/max_bot/instance.py`, а `error_handler` импортируется лениво внутри
`MessageSender.handle_send_error`. Подробности отличий Max от telegram — в
[src/max_bot/README.md](src/max_bot/README.md).

**Вебхуки.** Telegram проверяет секрет заголовком, у Max такого заголовка нет — поэтому его секрет
зашит в путь URL (`/max/webhook/{MAX_WEBHOOK_SECRET}`), см. `settings.max_webhook_url`. Секрет
отдельный от `SECRET_KEY`: путь попадает в логи веб-сервера и в реестр подписок Max, а `SECRET_KEY`
подписывает jwt-токены администраторов.

**Периодические задачи** — `job_queue` из python-telegram-bot, зарегистрированы в `create_bot()`
([src/bot/jobs.py](src/bot/jobs.py)): выдача ежедневного задания, напоминание о несданном отчёте,
автозавершение смены. Работают только когда запущен telegram-бот.

**Настройки** — pydantic v1 `BaseSettings` в [src/core/settings.py](src/core/settings.py),
кэшированный синглтон `settings`. При отсутствии `.env` подхватывается `.env.example`, поэтому
приложение стартует с примерными значениями вместо явной ошибки. Производные URL (вебхуки, форма
регистрации, строка подключения к БД) — свойства, собирайте их там, а не по месту.

**Домен.** Смена (`Shift`) содержит участников (`Member`), связывающих пользователя со сменой;
заявка на участие — `Request`; ежедневное задание — `Task`; фотоотчёт — `Report`; администраторы и
приглашения — `Administrator`/`AdministratorInvitation`. Награда участника — «ломбарьерчики»
(`numbers_lombaryers`). Статусы объявлены вложенными классами `Status(str, enum.Enum)` внутри модели.
Аналитические выгрузки в xlsx собирает `src/excel_generator/`.

## Ограничения, о которые легко споткнуться

- **pydantic заперт на 1.10** из-за fastapi ~0.89. API второй версии (`field_validator`,
  `model_dump`, `ConfigDict`) не использовать. По этой же причине для Max взята `aiomax`, а не
  официальная `maxapi`, которая требует pydantic v2.
- **Миграции с Enum**: создание и удаление типа в PostgreSQL приходится прописывать вручную —
  готовые рецепты и полный пример есть в разделе «Миграции с Enum-полем» в [README.md](README.md).
- **pre-commit запрещает коммиты в `master` и `develop`** и приводит переводы строк к CRLF.
- `src/api/request_models/request_base.py` и `src/api/response_models/healthcheck.py` содержат
  давние замечания flake8-docstrings — они не ваши, чинить их попутно не нужно.
