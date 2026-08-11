# Бот мессенджера Max: запуск и локальное тестирование

Основной бот проекта — telegram-бот (`src/bot/`). Модуль `src/max_bot/` добавляет
дополнительный канал — бота мессенджера [Max](https://dev.max.ru), который повторяет
сценарии основного бота: регистрация, фотоотчёты, баланс ломбарьеров, пропуск задания,
ежедневные рассылки и уведомления из админки.

Max-бот необязателен: если `MAX_BOT_TOKEN` не задан, он не запускается,
а telegram-бот и API работают в обычном режиме.

Используется библиотека [aiomax](https://github.com/dpnspn/aiomax).
Официальная `maxapi` не подходит: она требует pydantic v2, а проект работает на pydantic 1.10
(ограничение FastAPI 0.89).

## Отличия от основного telegram-бота

| | Telegram (основной) | Max (дополнительный) |
|---|---|---|
| Регистрация | WebApp-форма (`registration.html` + `tg.sendData`) | пошаговый диалог в чате (у Max Bridge нет аналога `sendData`) |
| Кнопки задания | reply-клавиатура | inline-кнопки на сообщении с заданием (reply-клавиатур в Max нет) |
| Идентификатор | `users.telegram_id` | `users.max_user_id` |
| Признак блокировки | `users.telegram_blocked` | `users.max_blocked` |

Пользователь приходит либо из telegram, либо из Max: `users.telegram_id` остаётся основным
идентификатором, а у пользователей из Max вместо него заполняется `users.max_user_id`
(наличие хотя бы одного проверяет constraint `users_messenger_id_check`).

Отправку сообщений выполняют методы `BotService.send_message` / `send_photo`
в [src/bots/bot_service.py](../bots/bot_service.py): telegram — поведение по умолчанию,
и только при заполненном `user.max_user_id` сообщение уходит через Max.

## 1. Получить токен Max-бота

Быстрый путь для разработки — через `@MasterBot` в мессенджере Max:

1. Найти `@MasterBot`, отправить `/create`.
2. Указать ник бота (латиница, оканчивается на `_bot`).
3. Указать отображаемое имя.
4. Скопировать выданный токен.

Официальный путь — [business.max.ru/self](https://business.max.ru/self) →
раздел «Чат-боты» → «Создать». Требуется верифицированный профиль юрлица, ИП или
самозанятого — резидента РФ; бот проходит модерацию до 48 часов, токен выдаётся после неё.

> **Note**:
> Без токена всё равно можно проверить миграцию, валидацию анкеты, фильтры и маршрутизацию
> уведомлений — см. раздел «[Проверка без токена Max](#7-проверка-без-токена-max)».

## 2. Установить зависимости

```shell
poetry install
```

```shell
poetry shell
```

> **Warning**:
> Проект рассчитан на Python 3.10. Под Python 3.11 не собирается `asyncpg 0.24.0`
> из lock-файла (нет готовых wheel-ов). Варианты: использовать Python 3.10
> (`poetry env use 3.10`) или поставить в окружение более новый asyncpg
> вручную — только для локальной работы, без изменения `poetry.lock`:
> `pip install asyncpg==0.29.0`.

## 3. Настроить переменные окружения

Скопировать `.env.example` в `.env` и задать значения:

```dotenv
BOT_TOKEN=<токен telegram-бота>
MAX_BOT_TOKEN=<токен Max-бота из шага 1>
MAX_BOT_WEBHOOK_MODE=False  # для локальной разработки — polling
MAX_BOT_USE_CERTIFICATE=False
APPLICATION_URL=http://localhost
DEBUG=True  # чтобы открывалась документация API на /api/docs
```

Если `MAX_BOT_TOKEN` пуст, Max-бот просто не запускается (в логах — предупреждение),
а telegram-бот и API работают как раньше.

> **Note**:
> Для соединения с `platform-api2.max.ru` может требоваться корневой сертификат Минцифры.
> Если запуск падает с ошибкой SSL — либо установить
> [сертификат](https://www.gosuslugi.ru/crt) в систему, либо задать
> `MAX_BOT_USE_CERTIFICATE=True` (тогда aiomax использует встроенный сертификат).

## 4. Поднять базу данных

```shell
docker compose -f docker-compose.local.yaml up -d
```

```shell
alembic upgrade head
```

Проверить, что появились поля Max-бота:

```shell
docker exec -it lomaya_baryery_local_postgres psql -U postgres -p 6100 -d lomaya_baryery_db_local -c "\d users"
```

Ожидаемо: `telegram_id` стал nullable, добавились `max_user_id` (unique) и `max_blocked`,
появился check-constraint `users_messenger_id_check`.

Наполнить базу тестовыми данными (в том числе создаётся администратор
`user@example.com` с паролем `string`):

```shell
python -m data_factory.main
```

## 5. Запустить приложение

API вместе с обоими ботами:

```shell
python run.py
```

Только боты, без API (оба в режиме polling):

```shell
python run_bot.py
```

Признак успешного старта Max-бота в логах:
`Started polling with bot @<ник> (<id>) - <имя>`.

## 6. Ручное тестирование

### 6.1 Подготовить смену

Регистрация возможна, только если есть смена в статусе `preparing` либо `started`,
начавшаяся не более `DAYS_FROM_START_OF_SHIFT_TO_JOIN` (по умолчанию 2) дней назад.
Иначе бот ответит ошибкой о невозможности регистрации.

Через документацию API (http://localhost/api/docs — доступна через nginx из
`docker-compose.local.yaml` при `DEBUG=True`):

1. `POST /administrators/login` — `user@example.com` / `string`, скопировать `access_token`.
2. Нажать «Authorize» и вставить токен.
3. `POST /shifts/` — создать смену, например `started_at` = сегодня, `finished_at` = +90 дней.

### 6.2 Сценарии в мессенджере Max

| # | Действие | Ожидаемый результат |
|---|---|---|
| 1 | Открыть диалог с ботом, нажать «Начать» | приветствие проекта + вопрос «Как тебя зовут?» |
| 2 | Отправить `A`, затем `John` | ошибка про минимум 2 символа, затем про кириллицу; вопрос повторяется |
| 3 | Дойти до даты, отправить `2015-09-01` | ошибка про формат ДД.ММ.ГГГГ |
| 4 | Отправить дату младше 3 лет | «Возраст не может быть менее 3 лет» |
| 5 | Город `ufa` | ошибка про кириллицу |
| 6 | Телефон `12345` | «Некорректный номер телефона» |
| 7 | Заполнить всё корректно | «Процесс регистрации занимает некоторое время…» |
| 8 | `/cancel` в середине диалога | «Заполнение данных прервано…» |
| 9 | `/start` повторно, пока заявка на рассмотрении | сообщение, что заявка уже рассматривается |
| 10 | `PATCH /requests/{id}/approve` в админке | в Max приходит уведомление о принятии в проект |
| 11 | `/start` после одобрения | сообщение, что участие уже подтверждено |
| 12 | `PATCH /shifts/{id}/start` | смена запущена |
| 13 | Дождаться рассылки заданий | приходит фото задания с кнопками «Пропустить задание» и «Баланс ломбарьеров» |
| 14 | Кнопка «Баланс ломбарьеров» | сообщение с количеством ломбарьерчиков |
| 15 | Кнопка «Пропустить задание» → «Пропустить» | текст сообщения заменяется на «Задание пропущено…» |
| 16 | Кнопка «Пропустить задание» → «Отмена» | текст заменяется на «Действие отменено» |
| 17 | Отправить фотографию | «Твой отчет отправлен на модерацию…», файл появляется в `static/user_reports/<shift_id>/<user_id>/` |
| 18 | Отправить документ или стикер | «Отчёт по заданию должен быть отправлен в виде фотографии.» |
| 19 | `PATCH /reports/{id}/approve` (или `/decline`) | в Max приходит уведомление о проверке задания |
| 20 | `PATCH /shifts/{id}/cancel` или `/finish` | приходит уведомление об отмене/завершении смены |
| 21 | Остановить бота в Max, затем отправить уведомление из админки | в БД `max_blocked = true`, в логах предупреждение о блокировке |
| 22 | Снова нажать «Начать» | `max_blocked` сбрасывается в `false` |
| 23 | Пройти регистрацию через telegram-бота | telegram-ветка работает как раньше (регресс-проверка) |

> **Note**:
> Чтобы не ждать 8 утра для проверки рассылки заданий (пункт 13), задайте
> `SEND_NEW_TASK_HOUR` на ближайший час и перезапустите приложение.
> Аналогично `SEND_NO_REPORT_REMINDER_HOUR` для проверки напоминания об отчёте.

### 6.3 Полезные SQL-запросы

```shell
docker exec -it lomaya_baryery_local_postgres psql -U postgres -p 6100 -d lomaya_baryery_db_local -c "SELECT name, surname, telegram_id, max_user_id, max_blocked, status FROM users WHERE max_user_id IS NOT NULL;"
```

## 7. Проверка без токена Max

### Миграция

SQL-скрипт миграции можно посмотреть без подключения к базе:

```shell
alembic upgrade d237eef85461:7f3a2b9c1d45 --sql
```

```shell
alembic downgrade 7f3a2b9c1d45:d237eef85461 --sql
```

### Валидация анкеты, фильтры и маршрутизация

Скрипт ниже не обращается ни к Max, ни к базе — проверяет валидацию шагов диалога,
регистрацию хендлеров, взаимоисключаемость фильтров и то, что уведомление
Max-пользователю уходит в Max-ветку. Сохранить как `check_max_bot.py` в корне проекта
и запустить `python check_max_bot.py`:

```python
import asyncio

from src.bots.bot_service import BotService
from src.core.db.models import User
from src.max_bot import handlers
from src.max_bot.handlers import router

# 1. Валидация шагов диалога регистрации
for field, value, valid in (
    ("name", "Артём", True),
    ("name", "John", False),
    ("date_of_birth", "01.09.2015", True),
    ("date_of_birth", "2015-09-01", False),
    ("city", "Ростов-на-Дону", True),
    ("phone_number", "+79170000000", True),
    ("phone_number", "12345", False),
):
    try:
        handlers._validate_registration_field(field, value)
        assert valid, f"{field}={value}: ожидалась ошибка"
    except ValueError as error:
        assert not valid, f"{field}={value}: неожиданная ошибка {error}"
print("валидация анкеты - ок")

# 2. Хендлеры и команды зарегистрированы
# (проверяются на роутере: экземпляр MaxBot создает aiohttp-сессию и требует event loop)
counts = {key: len(value) for key, value in router.handlers.items() if value}
assert counts["message_created"] == 3 and counts["message_callback"] == 4
assert counts["bot_started"] == 1 and sorted(router.commands) == ["cancel", "start"]
print(f"хендлеры - ок: {counts}, команды: {sorted(router.commands)}")

# 3. Уведомление Max-пользователю уходит в Max-ветку (бот не запущен - только warning в логах)
user = User()
user.max_user_id, user.max_blocked, user.telegram_id = 555, False, None
asyncio.run(BotService(type("App", (), {"bot": None})()).send_message(user, "тест"))
print("маршрутизация уведомлений - ок")
```

## 8. Режим webhook

Для локальной разработки достаточно polling. Если нужен именно webhook:

1. Поднять туннель с HTTPS (см. раздел «Использование Ngrok» в [README проекта](../../README.md)).
2. Задать переменные:

    ```dotenv
    MAX_BOT_WEBHOOK_MODE=True
    APPLICATION_URL=https://1234-56-78-9.ngrok.io  # адрес туннеля
    ```

3. Запустить `python run.py` — приложение само зарегистрирует подписку
   `POST /subscriptions` на адрес `{APPLICATION_URL}/api/max/webhook/{SECRET_KEY}`
   и снимет её при остановке.

> **Note**:
> У API Max нет аналога секретного заголовка telegram, поэтому секрет передаётся
> в пути вебхука. Значение берётся из `SECRET_KEY`.

> **Warning**:
> Max не позволяет одновременно использовать polling и webhook. При старте в режиме
> polling приложение снимает все существующие подписки — если один и тот же токен
> используется на нескольких стендах, они будут отключать вебхуки друг друга.
> Для разработки лучше завести отдельного бота.

## 9. Известные ограничения

* Состояние диалога регистрации хранится в памяти процесса: после перезапуска
  приложения незавершённый диалог сбрасывается, пользователь начинает с `/start`.
* Пользователь, зарегистрированный в telegram, при регистрации в Max с тем же номером
  телефона получит «Пользователь с таким номером телефона уже существует» —
  связывание аккаунтов не реализовано.
* Точный код ошибки API Max для заблокированного диалога (`access.denied` или
  `chat.not.found`) подтверждён только по документации библиотеки; список
  обрабатываемых ошибок — в `MaxBot.BLOCKING_ERRORS` ([main.py](main.py)), сама обработка
  общая для обоих ботов — в [src/bots/error_handler.py](../bots/error_handler.py).
