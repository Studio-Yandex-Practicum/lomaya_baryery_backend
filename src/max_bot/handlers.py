import enum
import uuid
from datetime import datetime
from urllib.parse import urljoin

import aiofiles
import aiohttp
import aiomax
from pydantic import ValidationError
from pydantic.error_wrappers import ValidationError as PydanticValidationError

from src.api.request_models.user import DATE_FORMAT, UserCreateRequest
from src.bot.api_services import get_user_service_callback
from src.core import exceptions
from src.core.db.db import get_session
from src.core.db.repository import (
    MemberRepository,
    ReportRepository,
    RequestRepository,
    ShiftRepository,
    TaskRepository,
    UserRepository,
)
from src.core.services.member_service import MemberService
from src.core.services.report_service import ReportService
from src.core.services.shift_service import ShiftService
from src.core.services.task_service import TaskService
from src.core.services.user_service import UserService
from src.core.settings import settings
from src.core.utils import get_lombaryers_for_quantity
from src.max_bot import ui

router = aiomax.Router()

START_TEXT = (
    "Это бот Центра \"Ломая барьеры\", который в игровой форме поможет "
    "особенному ребенку стать немного самостоятельнее! Выполняя задания "
    "каждый день, ребенок будет получать виртуальные \"ломбарьерчики\". "
    "В конце смены мы подведем итоги и наградим самых активных и старательных ребят!"
)
INVALID_DATE_FORMAT_TEXT = "Дата рождения должна быть в формате ДД.ММ.ГГГГ, например 01.09.2015."
TEXT_ONLY_ANSWER_TEXT = "Пожалуйста, отправь ответ текстовым сообщением."
CANCEL_REGISTRATION_TEXT = "Заполнение данных прервано. Отправь /start, чтобы начать заново."


class RegistrationState(str, enum.Enum):
    """Шаги диалога регистрации пользователя."""

    NAME = "registration_name"
    SURNAME = "registration_surname"
    DATE_OF_BIRTH = "registration_date_of_birth"
    CITY = "registration_city"
    PHONE_NUMBER = "registration_phone_number"


REGISTRATION_FIELD_BY_STATE = {
    RegistrationState.NAME: "name",
    RegistrationState.SURNAME: "surname",
    RegistrationState.DATE_OF_BIRTH: "date_of_birth",
    RegistrationState.CITY: "city",
    RegistrationState.PHONE_NUMBER: "phone_number",
}

NEXT_REGISTRATION_STATE = {
    RegistrationState.NAME: RegistrationState.SURNAME,
    RegistrationState.SURNAME: RegistrationState.DATE_OF_BIRTH,
    RegistrationState.DATE_OF_BIRTH: RegistrationState.CITY,
    RegistrationState.CITY: RegistrationState.PHONE_NUMBER,
    RegistrationState.PHONE_NUMBER: None,
}

REGISTRATION_PROMPTS = {
    RegistrationState.NAME: "Как тебя зовут? Напиши своё имя.",
    RegistrationState.SURNAME: "Напиши свою фамилию.",
    RegistrationState.DATE_OF_BIRTH: "Укажи дату рождения в формате ДД.ММ.ГГГГ, например 01.09.2015.",
    RegistrationState.CITY: "Из какого ты города?",
    RegistrationState.PHONE_NUMBER: "Укажи номер телефона, например +79000000000.",
}


def in_registration(message: aiomax.Message) -> bool:
    """Фильтр: пользователь находится в диалоге регистрации."""
    return isinstance(message.bot.storage.get_state(message.sender.user_id), RegistrationState)


def not_in_registration(message: aiomax.Message) -> bool:
    """Фильтр: пользователь не находится в диалоге регистрации."""
    return not in_registration(message)


def has_photo_attachment(message: aiomax.Message) -> bool:
    """Фильтр: в сообщении есть фотография."""
    attachments = message.body.attachments if message.body else None
    return bool(attachments) and any(isinstance(attachment, aiomax.PhotoAttachment) for attachment in attachments)


def has_non_photo_attachment(message: aiomax.Message) -> bool:
    """Фильтр: в сообщении есть вложения, но нет ни одной фотографии."""
    attachments = message.body.attachments if message.body else None
    return bool(attachments) and not any(isinstance(attachment, aiomax.PhotoAttachment) for attachment in attachments)


def _registration_prompt(state: RegistrationState, current_values: dict | None) -> str:
    """Построить текст вопроса для шага регистрации с текущим значением поля (при обновлении данных)."""
    prompt = REGISTRATION_PROMPTS[state]
    current_value = (current_values or {}).get(REGISTRATION_FIELD_BY_STATE[state])
    if current_value:
        prompt += f"\nТекущее значение: {current_value}. Отправь новое значение или повтори текущее."
    return prompt


def _validate_registration_field(field_name: str, raw_value: str) -> None:
    """Провалидировать одно поле анкеты валидаторами UserCreateRequest."""
    if field_name == "date_of_birth":
        try:
            datetime.strptime(raw_value, DATE_FORMAT)
        except ValueError:
            raise ValueError(INVALID_DATE_FORMAT_TEXT)
    field = UserCreateRequest.__fields__[field_name]
    _, error = field.validate(raw_value, {}, loc=field_name)
    if error:
        errors = error if isinstance(error, list) else [error]
        validation_error = PydanticValidationError(errors, UserCreateRequest)
        raise ValueError(
            "\n".join(
                item.get("msg", "Проверьте правильность заполнения данных.") for item in validation_error.errors()
            )
        )


async def _start_registration_dialog(max_user_id: int, send_callback, cursor: aiomax.fsm.FSMCursor) -> None:
    """Общий сценарий команды /start: приветствие и запуск диалога регистрации."""
    session = get_session()
    user_service = await get_user_service_callback(session)
    user = await user_service.get_user_by_max_id(max_user_id)
    if user and user.is_blocked:
        await user_service.unblock_user(user)
    await send_callback(START_TEXT)
    current_values = None
    if user:
        try:
            await user_service.check_before_change_user_data(user.id)
        except exceptions.ApplicationError as e:
            await send_callback(e.detail)
            return
        current_values = {
            "name": user.name,
            "surname": user.surname,
            "date_of_birth": user.date_of_birth.strftime(DATE_FORMAT),
            "city": user.city,
            "phone_number": user.phone_number,
        }
    cursor.change_data({"is_update": user is not None, "current": current_values, "fields": {}})
    cursor.change_state(RegistrationState.NAME)
    await send_callback(_registration_prompt(RegistrationState.NAME, current_values))


@router.on_bot_start()
async def start(payload: aiomax.BotStartPayload, cursor: aiomax.fsm.FSMCursor) -> None:
    """Нажатие кнопки "Начать" в диалоге с ботом."""
    await _start_registration_dialog(payload.user_id, payload.send, cursor)


@router.on_command("start")
async def start_command(ctx: aiomax.CommandContext, cursor: aiomax.fsm.FSMCursor) -> None:
    """Команда /start."""
    await _start_registration_dialog(ctx.sender.user_id, ctx.send, cursor)


@router.on_command("cancel")
async def cancel_command(ctx: aiomax.CommandContext, cursor: aiomax.fsm.FSMCursor) -> None:
    """Команда /cancel - прервать диалог регистрации."""
    cursor.clear()
    await ctx.send(CANCEL_REGISTRATION_TEXT)


@router.on_message(in_registration)
async def registration_dialog(message: aiomax.Message, cursor: aiomax.fsm.FSMCursor) -> None:
    """Пошаговый диалог заполнения регистрационных данных."""
    state = RegistrationState(cursor.get_state())
    data = cursor.get_data() or {"is_update": False, "current": None, "fields": {}}
    text = (message.body.text or "").strip()
    if not text:
        await message.send(TEXT_ONLY_ANSWER_TEXT)
        return
    field_name = REGISTRATION_FIELD_BY_STATE[state]
    try:
        _validate_registration_field(field_name, text)
    except ValueError as e:
        await message.send(f"Ошибка при заполнении данных:\n{e}")
        await message.send(_registration_prompt(state, data.get("current")))
        return
    data["fields"][field_name] = text
    cursor.change_data(data)
    next_state = NEXT_REGISTRATION_STATE[state]
    if next_state is not None:
        cursor.change_state(next_state)
        await message.send(_registration_prompt(next_state, data.get("current")))
        return
    await _finish_registration(message, cursor, data)


async def _finish_registration(message: aiomax.Message, cursor: aiomax.fsm.FSMCursor, data: dict) -> None:
    """Финальный шаг диалога: валидация анкеты целиком и создание (обновление) User и Request."""
    try:
        user_scheme = UserCreateRequest(**data["fields"])
    except ValidationError as e:
        error_text = "\n".join(
            tuple(error.get("msg", "Проверьте правильность заполнения данных.") for error in e.errors())
        )
        await message.send(f"Ошибка при заполнении данных:\n{error_text}")
        await _restart_registration_dialog(message, cursor, data)
        return
    user_scheme.max_user_id = message.sender.user_id
    session = get_session()
    registration_service = await get_user_service_callback(session)
    validation_error = False
    try:
        await registration_service.register_user(user_scheme)
    except exceptions.NotValidValueError as e:
        text = e.detail
        validation_error = True
    except exceptions.ApplicationError as e:
        text = e.detail
    else:
        text = "Процесс регистрации занимает некоторое время - вам придет уведомление."
        if data.get("is_update"):
            text = (
                "Обновленные данные приняты!\n"
                "Процесс обработки заявок занимает некоторое время - вам придет уведомление."
            )
    cursor.clear()
    await message.send(text)
    if validation_error:
        await _restart_registration_dialog(message, cursor, data)


async def _restart_registration_dialog(message: aiomax.Message, cursor: aiomax.fsm.FSMCursor, data: dict) -> None:
    """Перезапустить диалог, показывая ранее введенные значения (аналог префилла формы в telegram)."""
    current_values = {**(data.get("current") or {}), **data.get("fields", {})}
    cursor.change_data({"is_update": data.get("is_update", False), "current": current_values, "fields": {}})
    cursor.change_state(RegistrationState.NAME)
    await message.send(_registration_prompt(RegistrationState.NAME, current_values))


async def download_photo_report(photo: aiomax.PhotoAttachment, shift_user_dir: str) -> str:
    """Сохранить фото отчёта на диск."""
    file_name = f"{uuid.uuid4().hex}.jpg"
    file_path = f"{shift_user_dir}/{file_name}"
    (settings.USER_REPORTS_DIR / shift_user_dir).mkdir(parents=True, exist_ok=True)
    async with aiohttp.ClientSession() as session:
        async with session.get(photo.url) as response:
            response.raise_for_status()
            content = await response.read()
    async with aiofiles.open(settings.USER_REPORTS_DIR / file_path, "wb") as file:
        await file.write(content)
    return file_path


@router.on_message(has_photo_attachment, not_in_registration)
async def photo_handler(message: aiomax.Message) -> None:
    """Обработка полученного фото."""
    session_gen = get_session()
    session = await session_gen.asend(None)
    shift_repository = ShiftRepository(session)
    user_service = UserService(UserRepository(session), RequestRepository(session))
    report_service = ReportService(ReportRepository(session), shift_repository, MemberRepository(session))
    shift_service = ShiftService(shift_repository)

    text = "Твой отчет отправлен на модерацию, после проверки тебе придет уведомление."

    try:
        user = await user_service.get_user_by_max_id(message.sender.user_id)
        if user is None:
            await message.send("Ты еще не зарегистрирован в проекте. Отправь /start, чтобы зарегистрироваться.")
            return
        report = await report_service.get_current_report(user.id)
        shift_dir = await shift_service.get_shift_dir(report.shift_id)
        photo = next(
            attachment for attachment in message.body.attachments if isinstance(attachment, aiomax.PhotoAttachment)
        )
        file_path = await download_photo_report(photo, f"{shift_dir}/{user.id}")
        photo_url = urljoin(settings.USER_REPORTS_URL, file_path)
        await report_service.send_report(report, photo_url)
    except exceptions.ApplicationError as e:
        text = e.detail

    await message.send(text)


@router.on_message(has_non_photo_attachment, not_in_registration)
async def incorrect_report_type_handler(message: aiomax.Message) -> None:
    """Отправка пользователю предупреждения о несоответствии типа данных ожидаемому."""
    await message.send("Отчёт по заданию должен быть отправлен в виде фотографии.")


@router.on_button_callback(ui.BALANCE_CALLBACK)
async def balance_callback(callback: aiomax.Callback) -> None:
    """Нажатие кнопки баланса ломбарьеров."""
    amount = await get_balance(callback.user.user_id)
    await callback.send(
        f"Общее количество {amount} {get_lombaryers_for_quantity(amount)}! "
        f"Выполняй задания каждый день и не забывай отправлять фотоотчет! Ты молодец!"
    )


@router.on_button_callback(ui.SKIP_TASK_CALLBACK)
async def skip_task_callback(callback: aiomax.Callback) -> None:
    """Нажатие кнопки пропуска задания: запрос подтверждения."""
    await callback.send(
        "Тобой была нажата кнопка \"пропустить задание\". "
        "Если ты пропустишь задание, то не сможешь отправить отчёт сегодня.",
        keyboard=ui.CONFIRM_SKIP_TASK_KEYBOARD,
    )


@router.on_button_callback(ui.CONFIRM_SKIP_TASK_CALLBACK)
async def confirm_skip_task_callback(callback: aiomax.Callback) -> None:
    """Подтверждение пропуска задания."""
    try:
        await skip_report(callback.user.user_id)
    except exceptions.ApplicationError as e:
        text = e.detail
    else:
        text = f"Задание пропущено, следующее задание придет в {settings.FORMATTED_TASK_TIME} часов утра."
    await callback.bot.edit_message(callback.message.id, text=text)


@router.on_button_callback(ui.CANCEL_SKIP_TASK_CALLBACK)
async def cancel_skip_task_callback(callback: aiomax.Callback) -> None:
    """Отмена пропуска задания."""
    await callback.bot.edit_message(callback.message.id, text="Действие отменено")


async def get_balance(max_user_id: int) -> int:
    """Метод для получения баланса ломбарьеров."""
    session_gen = get_session()
    session = await session_gen.asend(None)
    member_service = MemberService(MemberRepository(session))
    return await member_service.get_number_of_lombariers_by_max_user_id(max_user_id)


async def skip_report(max_user_id: int) -> None:
    """Метод для пропуска задания."""
    session_gen = get_session()
    session = await session_gen.asend(None)
    shift_repository = ShiftRepository(session)
    shift_service = ShiftService(shift_repository)
    user_service = UserService(UserRepository(session), RequestRepository(session), shift_service)
    task_service = TaskService(TaskRepository(session))
    report_service = ReportService(ReportRepository(session), shift_repository, MemberRepository(session), task_service)
    user = await user_service.get_user_by_max_id(max_user_id)
    await report_service.skip_current_report(user.id)


async def bot_stopped_handler(update: dict) -> None:
    """Пользователь остановил (заблокировал) бота: отмечает блокировку в базе."""
    max_user_id = (update.get("user") or {}).get("user_id")
    if max_user_id is None:
        return
    session = get_session()
    user_service = await get_user_service_callback(session)
    user = await user_service.get_user_by_max_id(max_user_id)
    if user is None:
        return
    await user_service.block_user(user)
