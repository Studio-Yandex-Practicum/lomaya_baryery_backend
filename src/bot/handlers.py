import json

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    WebAppInfo,
)
from telegram.ext import CallbackContext, ContextTypes

from src.api.request_models.photo import PhotoCreateRequest
from src.api.request_models.user_task import UserTaskUpdateRequest
from src.bot.services import download_photo_report_callback, get_registration_service_callback
from src.core.db.db import get_session
from src.core.db.repository import PhotoRepository, UserRepository, UserTaskRepository
from src.core.services.photo_service import PhotoService
from src.core.services.user_task_service import UserTaskService
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

    await context.bot.send_message(chat_id=update.effective_chat.id, text=start_text)


async def register(update: Update, context: CallbackContext) -> None:
    """Инициализация формы регистрации."""
    await update.message.reply_text(
        "Нажмите на кнопку ниже, чтобы перейти на форму регистрации.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Зарегистрироваться в проекте",
                web_app=WebAppInfo(url=settings.APPLICATION_URL + "/lomaya_baryery_backend/src/html/registration.html"),
            )
        ),
    )


async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Получение данных из формы регистрации. Создание объекта User и Request."""
    user_data = json.loads(update.effective_message.web_app_data.data)
    try:
        user_data["telegram_id"] = update.effective_user.id
        session = get_session()
        registration_service = await get_registration_service_callback(session)
        await registration_service.user_registration(user_data)
        await update.message.reply_text(
            text="Процесс регистрации занимает некоторое время - вам придет уведомление",
            reply_markup=ReplyKeyboardRemove(),
        )
    except ValidationError as e:
        await update.message.reply_text(f"Ошибка при валидации данных: {e}")


async def photo_handler(update: Update, context: CallbackContext) -> None:
    """Обработка полученного фото."""
    url = await download_photo_report_callback(update, context)
    photo_obj = PhotoCreateRequest(url=url)

    session_gen = get_session()
    session = await session_gen.asend(None)
    photo_service = PhotoService(PhotoRepository(session))
    try:
        photo = await photo_service.create_new_photo(photo_obj)
        await update.message.reply_text("Отчёт отправлен на проверку.")

        user_service = UserService(UserRepository(session))
        user = await user_service.get_user_by_telegram_id(update.effective_chat.id)

        user_task_service = UserTaskService(UserTaskRepository(session))
        user_task = await user_task_service.get_user_task_to_change_status_photo_id(user.id)
        if user_task:
            update_user_task_dict = {
                "status": "under_review",
                "photo_id": photo.id,
            }
            user_task = await user_task_service.update_user_task(
                user_task.id, UserTaskUpdateRequest(**update_user_task_dict)
            )
    except IntegrityError:
        await update.message.reply_text("Отчёт уже есть в системе.")
