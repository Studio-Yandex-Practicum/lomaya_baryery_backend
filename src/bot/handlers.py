from sqlalchemy.exc import IntegrityError
from telegram import Update
from telegram.ext import CallbackContext

from src.api.request_models.photo import PhotoCreateRequest
from src.api.request_models.user_task import UserTaskUpdateRequest
from src.bot.services import download_photo_report_callback
from src.core.db.db import get_session
from src.core.db.repository import PhotoRepository, UserRepository, UserTaskRepository
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
