from sqlalchemy.exc import IntegrityError
from telegram import Update
from telegram.ext import CallbackContext

from src.api.request_models.photo import PhotoCreateRequest
from src.bot.services import download_photo_report_callback
from src.core.db.db import get_session
from src.core.db.models import UserTask
from src.core.db.repository import PhotoRepository, UserRepository
from src.core.services.photo_service import PhotoService
from src.core.services.user_task_service import UserTaskService
from src.core.services.user_service import UserService


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


async def photo_handler(update: Update, context: CallbackContext) -> None:
    """Обработка полученного фото."""
    url = await download_photo_report_callback(update, context)

    photo_data = {"url": url}
    photo_obj = PhotoCreateRequest(**photo_data)

    sessions = get_session()
    async for session in sessions:
        photo_repository = PhotoRepository(session)
        photo_service = PhotoService(photo_repository)
        try:
            photo = await photo_service.create_new_photo(photo_obj)
            await update.message.reply_text("Отчёт отправлен на проверку.")

            user_repository = UserRepository(session)
            user_service = UserService(user_repository)
            user = await user_service.get_user_by_telegram_id(update.effective_chat.id)
            user_task = await UserTaskService(session).get_user_task_to_change(user.id)
            if user_task:
                user_task = await UserTaskService(session).change_status(user_task, UserTask.Status.UNDER_REVIEW)
                user_task = await UserTaskService(session).change_photo_id(user_task, photo.id)
        except IntegrityError:
            await update.message.reply_text("Отчёт уже есть в системе.")
