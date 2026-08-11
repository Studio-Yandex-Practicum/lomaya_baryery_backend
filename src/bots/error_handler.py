import logging

from src.bots.services import MessageSender
from src.core.db.db import get_session
from src.core.db.models import User
from src.core.db.repository import RequestRepository, UserRepository
from src.core.services.user_service import UserService


async def error_handler(sender: MessageSender, user: User, error: Exception) -> None:
    """Обработать ошибку отправки сообщения участнику.

    Если ошибка мессенджера означает, что пользователь заблокировал бота, отметить это
    в базе, иначе передать ошибку дальше.
    """
    if not sender.is_blocking_error(error):
        raise error
    session_gen = get_session()
    session = await session_gen.asend(None)
    user_service = UserService(UserRepository(session), RequestRepository(session))
    await sender.set_user_blocked(user_service, user)
    reason = str(error) or type(error).__name__
    logging.warning(f"Произведена блокировка пользователя: {user}. Причина блокировки: {reason}")
