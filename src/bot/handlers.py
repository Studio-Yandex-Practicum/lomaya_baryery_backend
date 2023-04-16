import json
import urllib
from pathlib import Path
from urllib.parse import urljoin

from pydantic import ValidationError
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    KeyboardButton,
    MenuButtonWebApp,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    WebAppInfo,
)
from telegram.ext import CallbackContext

from src.api.request_models.user import UserCreateRequest, UserWebhookTelegram
from src.bot.api_services import get_user_service_callback
from src.bot.ui import LOMBARIERS_BALANCE, SKIP_A_TASK
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
    context.user_data["user"] = user
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
    query = None
    text = "Зарегистрироваться в проекте"
    if update.effective_message.web_app_data:
        query = urllib.parse.urlencode(json.loads(update.effective_message.web_app_data.data))
        text = "Исправить неверно внесенные данные"
    await update.message.reply_text(
        "Нажмите на кнопку ниже, чтобы перейти на форму регистрации.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text=text,
                web_app=WebAppInfo(url=f"{settings.registration_template_url}?{query}"),
            )
        ),
    )
    await context.bot.set_chat_menu_button(
        chat_id=update.message.chat.id,
        menu_button=MenuButtonWebApp(
            text="Форма регистрации",
            web_app=WebAppInfo(url=f"{settings.registration_template_url}?{query}"),
        ),
    )
    inline_message = await update.effective_message.reply_text(
        "\N{white down pointing backhand index}" * 4,
        reply_markup=InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(
                text=text,
                web_app=WebAppInfo(url=f"{settings.registration_template_url}?{query}"),
            )
        ),
    )
    context.chat_data["inline_message"] = inline_message


async def update_user_data(
    update: Update,
    context: CallbackContext,
) -> None:
    """Инициализация формы для обновления регистрационных данных пользователя."""
    if update.effective_message.web_app_data:
        query = urllib.parse.urlencode(json.loads(update.effective_message.web_app_data.data))
        text = "Исправить неверно внесенные данные"
    else:
        text = "Подать заявку на участие в смене"
        user = context.user_data.get("user")
        web_hook = UserWebhookTelegram.from_orm(user)
        query = urllib.parse.urlencode({"update": "true"} | web_hook.dict())
    await update.message.reply_text(
        "Нажмите на кнопку ниже, чтобы перейти на форму регистрации.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text=text,
                web_app=WebAppInfo(url=f"{settings.registration_template_url}?{query}"),
            )
        ),
    )
    await context.bot.set_chat_menu_button(
        chat_id=update.message.chat.id,
        menu_button=MenuButtonWebApp(
            text="Форма регистрации",
            web_app=WebAppInfo(url=f"{settings.registration_template_url}?{query}"),
        ),
    )
    inline_message = await update.effective_message.reply_text(
        "\N{white down pointing backhand index}" * 4,
        reply_markup=InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(
                text=text,
                web_app=WebAppInfo(url=f"{settings.registration_template_url}?{query}"),
            )
        ),
    )
    context.chat_data["inline_message"] = inline_message


async def web_app_data(update: Update, context: CallbackContext) -> None:
    """Получение данных из формы регистрации. Создание (обновление) объекта User и Request."""
    if not update.effective_message.web_app_data:
        user_data = context.bot_data[update.effective_user.id]
    else:
        user_data = json.loads(update.effective_message.web_app_data.data)
    try:
        user_scheme = UserCreateRequest(**user_data)
    except ValidationError as e:
        e = "\n".join(tuple(error.get("msg", "Проверьте правильность заполнения данных.") for error in e.errors()))
        await update.message.reply_text(f"Ошибка при заполнении данных:\n{e}")
        if context.user_data.get("user"):
            await update_user_data(update, context)
        else:
            await register_user(update, context)
        return
    user_scheme.telegram_id = update.effective_user.id
    session = get_session()
    registration_service = await get_user_service_callback(session)
    reply_markup, text, validation_error = None, "Что-то пошло не так", False
    try:
        await registration_service.register_user(user_scheme)
    except exceptions.NotValidValueError as e:
        text = e.detail
        validation_error = True
    except exceptions.ApplicationError as e:
        text = e.detail
    else:
        text = "Процесс регистрации занимает некоторое время - вам придет уведомление."
        if context.user_data.get('user'):
            text = (
                "Обновленные данные приняты!\n"
                "Процесс обработки заявок занимает некоторое время - вам придет уведомление."
            )
        reply_markup = ReplyKeyboardRemove()
        await context.bot.set_chat_menu_button(
            chat_id=update.message.chat.id,
            menu_button=None,
        )
        await context.bot.edit_message_reply_markup(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data["inline_message"].message_id,
        )
    finally:
        await update.message.reply_text(
            text=text,
            reply_markup=reply_markup,
        )
        if validation_error and context.user_data.get("user"):
            await update_user_data(update, context)
        elif validation_error:
            await register_user(update, context)


async def get_web_app_query_data(update: dict, context: CallbackContext) -> None:
    """Получение данных из формы регистрации, запущенной с inline-, menu- кнопки."""
    web_app_query_id = update.get("query_id")
    context.bot_data[update.get("user_id")] = update.get("data")
    await context.bot.answer_web_app_query(
        web_app_query_id=web_app_query_id,
        result=InlineQueryResultArticle(
            id=web_app_query_id,
            title="Данные отправлены",
            input_message_content=InputTextMessageContent(
                "Данные успешно отправлены боту",
            ),
        ),
    )


async def get_answer_web_app(update: Update, context: CallbackContext) -> None:
    """Обработка ответа бота после отправки данных пользователя с ипользованием inline-, menu- кнопки."""
    if "Ошибка при заполнении данных" in update.effective_message.text:
        if context.user_data.get("user"):
            await update_user_data(update, context)
        else:
            await register_user(update, context)
        return
    if "Процесс регистрации занимает некоторое время - вам придет уведомление" in update.effective_message.text:

        await context.bot.set_chat_menu_button(
            chat_id=update.message.chat.id,
            menu_button=None,
        )
        await context.bot.edit_message_reply_markup(
            chat_id=update.effective_chat.id,
            message_id=context.chat_data["inline_message"].message_id,
        )
        crutch = await update.message.reply_text(
            text=".",
            reply_markup=ReplyKeyboardRemove(),
        )
        await crutch.delete()


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

    text = "Твой отчет отправлен на модерацию, после проверки тебе придет уведомление."

    try:
        user = await user_service.get_user_by_telegram_id(update.effective_chat.id)
        report = await report_service.get_current_report(user.id)
        shift_dir = await shift_service.get_shift_dir(report.shift_id)
        file_path = await download_photo_report_callback(update, context, f"{shift_dir}/{user.id}")
        photo_url = urljoin(settings.user_reports_url, file_path)
        await report_service.send_report(report, photo_url)
    except exceptions.ApplicationError as e:
        text = e.detail

    await update.message.reply_text(text)


async def button_handler(update: Update, context: CallbackContext) -> None:
    if update.message.text == LOMBARIERS_BALANCE:
        amount = await get_balance(update.effective_chat.id)
        await update.message.reply_text(
            f"Общее количество {amount} {get_lombaryers_for_quantity(amount)}! "
            f"Выполняй задания каждый день и не забывай отправлять фотоотчет! Ты молодец!"
        )

    if update.message.text == SKIP_A_TASK:
        try:
            await skip_report(update.effective_chat.id)
        except exceptions.ReportAlreadyReviewedException:
            text = "Ранее отправленный отчет проверяется или уже принят, сейчас нельзя пропустить задание."
        except exceptions.ApplicationError as e:
            text = e.detail
        else:
            text = f"Задание пропущено, следующее задание придет в {settings.formatted_task_time} часов утра."
        await update.message.reply_text(text)


async def get_balance(telegram_id: int) -> int:
    """Метод для получения баланса ломбарьеров."""
    session_gen = get_session()
    session = await session_gen.asend(None)
    member_service = MemberService(MemberRepository(session))
    return await member_service.get_number_of_lombariers_by_telegram_id(telegram_id)


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
