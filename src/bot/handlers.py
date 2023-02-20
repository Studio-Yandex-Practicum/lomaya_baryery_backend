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
from src.core.db.db import get_session
from src.core.db.repository import (
    MemberRepository,
    ReportRepository,
    RequestRepository,
    ShiftRepository,
    UserRepository,
)
from src.core.exceptions import (
    CannotAcceptReportError,
    CurrentTaskNotFoundError,
    DuplicateReportError,
    ExceededAttemptsReportError,
    RegistrationException,
)
from src.core.services.report_service import ReportService
from src.core.services.shift_service import ShiftService
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
        await update_user_data(update, context)
    else:
        await register_user(update, context)


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
                web_app=WebAppInfo(url=f"{settings.registration_template_url}"),
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
                web_app=WebAppInfo(url=f"{settings.registration_template_url}?{query}"),
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
    if context.user_data.get('user'):
        text = (
            " Обновленные данные приняты!\nПроцесс обработки заявок занимает некоторое время - вам придет уведомление."
        )
    await update.message.reply_text(
        text=text,
        reply_markup=ReplyKeyboardRemove(),
    )
    try:
        await registration_service.register_user(user_scheme)
    except RegistrationException as e:
        await update.message.reply_text(text=e.detail, reply_markup=ReplyKeyboardRemove())


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
        await update.message.reply_text("Отчёт отправлен на проверку.")
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


async def incorrect_report_type_handler(update: Update, context: CallbackContext) -> None:
    """Отправка пользователю предупреждения о несоответствии типа данных ожидаемому."""
    await update.message.reply_text("Отчёт по заданию должен быть отправлен в виде фотографии.")
