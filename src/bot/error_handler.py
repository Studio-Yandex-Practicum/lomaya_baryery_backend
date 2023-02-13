from telegram.error import TelegramError
from telegram.ext import ContextTypes

from src.core.db.db import get_session
from src.core.db.repository import RequestRepository, UserRepository
from src.core.services.user_service import UserService


async def error_handler(update: object, context: ContextTypes) -> None:
    if isinstance(context, dict):
        error = context['error']
        chat_id = context['chat_id']
    else:
        error = context.error
        chat_id = context._chat_id

    if isinstance(error, TelegramError) and error.message in (
        'Forbidden: bot was blocked by the user',
        'Chat not found',
    ):
        session_gen = get_session()
        session = await session_gen.asend(None)
        user_service = UserService(UserRepository(session), RequestRepository(session))
        user = await user_service.get_user_by_telegram_id(chat_id)
        await user_service.set_telegram_blocked(user)
    else:
        raise error
