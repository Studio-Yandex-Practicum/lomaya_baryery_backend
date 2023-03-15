import json
import urllib
from pathlib import Path
from urllib.parse import urljoin

from pydantic import ValidationError
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    WebAppInfo,
)
from telegram.ext import CallbackContext

from src.api.request_models.user import UserCreateRequest, UserWebhookTelegram
from src.bot.api_services import get_user_service_callback
from src.bot.jobs import LOMBARIERS_BALANCE, SKIP_A_TASK
from src.core.db.db import get_session
from src.core.db.repository import (
    MemberRepository,
    ReportRepository,
    RequestRepository,
    ShiftRepository,
    TaskRepository,
    UserRepository,
)
from src.core.exceptions import (
    ApplicationError,
    CannotAcceptReportError,
    CurrentTaskNotFoundError,
    DuplicateReportError,
    ExceededAttemptsReportError,
    ReportAlreadyReviewedException,
    ReportSkippedError,
)
from src.core.services.member_service import MemberService
from src.core.services.report_service import ReportService
from src.core.services.shift_service import ShiftService
from src.core.services.task_service import TaskService
from src.core.services.user_service import UserService
from src.core.settings import settings


async def start(update: Update, context: CallbackContext) -> None:
    """Команда /start."""
    start_text = (
        "Это бот Центра \"Ломая барьеры\", который в игровой форме поможет "
        "особенному ребенку стать немного самостоятельнее! Выполняя задания "
        "каждый день, ребенку будут начислять виртуальные \"ломбарьерчики\". "
        "Каждый месяц мы будем подводить итоги "
        "и награждать самых активных и старательных ребят!"
    )
    session = get_session()
    user_service = await get_user_service_callback(session)
    user = await user_service.get_user_by_telegram_id(update.effective_chat.id)
    context.user_data['user'] = user
    if user and user.telegram_blocked:
        await user_service.unset_telegram_blocked(user)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=start_text)
    if user:
        await check_user_status(user, update, context)
    else:
        await register_user(update, context)


async def check_user_status(update: Update, context: CallbackContext) -> None:
    """Проверка статуса пользователя и отправка соответствующего сообщения."""
    if context.user_data.get('user').status is None or context.user_data.get('user').status == 'declined':
        await update_user_data(update, context)
    else:
        if context.user_data.get('user').status == 'pending':
            await update.message.reply_text(
                "Ваша заявка еще на рассмотрении.")
        elif context.user_data.get('user').status == 'approved':
            await update.message.reply_text(
                "Ваша заявка уже одобрена и не может быть изменена.")


async def register_user(
    update: Update,
    context: CallbackContext,
) -> None:
    """Инициализация формы регистрации пользователя."""
    await update.message.reply_text(
        "Нажмите на кнопку ниже, чтобы перейти на форму регистрации.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Зарегистрироваться в проекте",
                web_app=WebAppInfo(url=settings.registration_template_url),
            )
        ),
    )


async def update_user_data(
    update: Update,
    context: CallbackContext,
) -> None:
    """Инициализация формы для обновления регистрационных данных пользователя."""
    user = context.user_data.get('user')
    web_hook = UserWebhookTelegram.from_orm(user)
    query = urllib.parse.urlencode(web_hook.dict())
    await update.message.reply_text(
        "Нажмите на кнопку ниже, чтобы перейти на форму регистрации.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Подать заявку на участие в смене",
                web_app=WebAppInfo(
                    url=f'{settings.registration_template_url}?{query}'),
            )
        ),
    )


async def web_app_data(update: Update, context: CallbackContext) -> None:
    """Получение данных из формы регистрации. Создание (обновление) объекта User и Request."""
    user_data = json.loads(update.effective_message.web_app_data.data)
    try:
        user_scheme = UserCreateRequest(**user_data)
    except ValidationError as e:
        e = "\n".join(tuple(error.get("msg", "Проверьте правильность заполнения данных.") for error in e.errors()))
        await update.message.reply_text(f"Ошибка при заполнении данных:\n{e}")
        return
    user_scheme.telegram_id = update.effective_user.id
    session = get_session()
    registration_service = await get_user_service_callback(session)
    text = "Процесс регистрации занимает некоторое время - вам придет уведомление."
    if user_scheme.telegram_id != update.effective_user.id:
        if context.user_data.get('user').status is None or context.user_data.get('user').status == 'declined':
            await update.message.reply_text(
                "Вы пытаетесь завершить регистрацию с другого устройства."
                "Пожалуйста, повторите попытку с устройства, с которого начали регистрацию."
            )
            return
    if context.user_data.get('user'):
        text = (
            " Обновленные данные приняты!\nПроцесс обработки заявок занимает некоторое время - вам придет уведомление."
        )
    try:
        await registration_service.register_user(user_scheme)
    except ApplicationError as e:
        text = e.detail
    await update.message.reply_text(
        text=text,
        reply_markup=ReplyKeyboardRemove(),
    )


async def download_photo_report_callback(update: Update, context: CallbackContext, shift_user_dir: str) -> str:
    """Сохранить фото отчёта на диск."""
    file = await update.message.photo[-1].get_file()
    file_name = file.file_unique_id + Path(file.file_path).suffix
    file_path = f"{shift_user_dir}/{file_name}"
    await file.download_to_drive(custom_path=(settings.user_reports_dir / file_path))
    return file_path


async def photo_handler(update: Update, context: CallbackContext) -> None:
    """Обработка полученного фото."""
    session_gen = get_session()
    session = await session_gen.asend(None)
    user_service = UserService(UserRepository(session), RequestRepository(session))
    report_service = ReportService(ReportRepository(session), ShiftRepository(session), MemberRepository(session))
    shift_service = ShiftService(ShiftRepository(session))
    user = await user_service.get_user_by_telegram_id(update.effective_chat.id)
    report = await report_service.get_current_report(user.id)
    shift_dir = await shift_service.get_shift_dir(report.shift_id)
    file_path = await download_photo_report_callback(update, context, f"{shift_dir}/{user.id}")
    photo_url = urljoin(settings.user_reports_url, file_path)

    try:
        await report_service.send_report(report, photo_url)
        await update.message.reply_text("Твой отчет отправлен на модерацию, после проверки тебе придет уведомление.")
    except CurrentTaskNotFoundError:
        await update.message.reply_text("Сейчас заданий нет.")
    except CannotAcceptReportError:
        await update.message.reply_text(
            "Ранее отправленный отчет проверяется или уже принят. Новые отчеты сейчас не принимаются."
        )
    except DuplicateReportError:
        await update.message.reply_text(
            "Данная фотография уже использовалась в другом отчёте. Пожалуйста, загрузите другую фотографию."
        )
    except ExceededAttemptsReportError:
        await update.message.reply_text(
            "Превышено количество попыток сдать отчет."
            "Предлагаем продолжить, ведь впереди много интересных заданий. "
            "Следующее задание придет в 8.00 мск."
        )
    except ReportSkippedError:
        await update.message.reply_text("Задание было пропущено, следующее задание придет в 8.00 мск.")


async def button_handler(update: Update, context: CallbackContext) -> None:
    if update.message.text == LOMBARIERS_BALANCE:
        amount = await balance(update.effective_chat.id)
        await update.message.reply_text(f"Количество ломбарьеров = {amount}.")
    if update.message.text == SKIP_A_TASK:
        try:
            await skip_report(update.effective_chat.id)
            await update.message.reply_text("Задание пропущено, следующее задание придет в 8.00 мск.")
        except CurrentTaskNotFoundError:
            await update.message.reply_text("Сейчас заданий нет.")
        except ReportAlreadyReviewedException:
            await update.message.reply_text(
                "Ранее отправленный отчет проверяется или уже принят, сейчас нельзя пропустить задание."
            )
        except ReportSkippedError:
            await update.message.reply_text("Задание было пропущено, следующее задание придет в 8.00 мск.")


async def balance(telegram_id: int) -> int:
    """Метод для получения баланса ломбарьеров."""
    session_gen = get_session()
    session = await session_gen.asend(None)
    member_service = MemberService(MemberRepository(session))
    member = await member_service.get_by_user_id(telegram_id)
    return member.numbers_lombaryers


async def skip_report(chat_id: int) -> None:
    """Метод для пропуска задания."""
    session_gen = get_session()
    session = await session_gen.asend(None)
    shift_service = ShiftService(ShiftRepository(session))
    user_service = UserService(UserRepository(session), RequestRepository(session), shift_service)
    task_service = TaskService(TaskRepository(session))
    report_service = ReportService(
        ReportRepository(session), ShiftRepository(session), MemberRepository(session), task_service
    )
    user = await user_service.get_user_by_telegram_id(chat_id)
    await report_service.skip_current_report(user.id)


async def incorrect_report_type_handler(update: Update, context: CallbackContext) -> None:
    """Отправка пользователю предупреждения о несоответствии типа данных ожидаемому."""
    await update.message.reply_text("Отчёт по заданию должен быть отправлен в виде фотографии.")
