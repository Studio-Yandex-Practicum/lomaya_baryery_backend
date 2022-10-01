import json
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    WebAppInfo,
)
from telegram.ext import CallbackContext, ContextTypes
from pydantic import ValidationError

from src.bot.services import is_user_valid_for_registration, registration
from src.core.utils import get_url


async def start(update: Update, context: CallbackContext) -> None:
    """Команда /start."""
    start_text = (
        'Это бот Центра "Ломая барьеры", который в игровой форме поможет '
        'особенному ребенку стать немного самостоятельнее! Выполняя задания '
        'каждый день, ребенку будут начислять виртуальные "ломбарьерчики". '
        'Каждый месяц мы будем подводить итоги '
        'и награждать самых активных и старательных ребят!'
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=start_text
    )


async def registration_form_init(update: Update,
                                 context: CallbackContext) -> None:
    """Инициализация формы регистрации."""
    valid_user = await is_user_valid_for_registration(
        telegram_id=update.effective_user.id
    )
    if not valid_user:
        return

    await update.message.reply_text(
        "Нажмите на кнопку ниже, чтобы перейти на форму регистрации.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Зарегистрироваться в проекте",
                web_app=WebAppInfo(
                    url=get_url('registration.html')),
            )
        ),
    )


async def web_app_data(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> None:
    """Получение данных из формы регистрации.
    Создание объекта User и Request."""
    user_data = json.loads(update.effective_message.web_app_data.data)
    try:
        user_data['telegram_id'] = update.effective_user.id
        await registration(user_data)
        await update.message.reply_text(
            text=f"Процесс регистрации занимает некоторое время - "
                 f"вам придет уведомление",
            reply_markup=ReplyKeyboardRemove(),
        )
    except ValidationError as e:
        await update.message.reply_text(
            f'Ошибка при валидации данных: {e}')
