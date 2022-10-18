import json

from pydantic import ValidationError
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    WebAppInfo,
)
from telegram.ext import CallbackContext, ContextTypes

from src.bot.api_services import get_registration_service_callback
from src.core.db.db import get_session
from src.core.services.user_task_service import get_current_user_task_by_telegram_id
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


async def change_task_status_handler(
    update: Update,
    context: CallbackContext,
) -> None:
    """Уведомление о проверенном задании."""
    user_task = await get_current_user_task_by_telegram_id(update.effective_chat.id)
    if user_task.status in ("approved", "declined"):
        if user_task.status == "approved":
            text_reply = f"""
            Твой отчет от {user_task.photo.updated_at} принят!
            Тебе начислен 1 \"ломбарьерчик\".
            Следующее задание придет в 8.00 мск.
            """
        else:
            text_reply = """
                К сожалению, мы не можем принять твой фотоотчет!
                Возможно на фотографии не видно, что именно ты выполняешь задание.
                Предлагаем продолжить, ведь впереди много интересных заданий.
                Следующее задание придет в 8.00 мск.
            """
        await update.message.reply_text(text_reply)
