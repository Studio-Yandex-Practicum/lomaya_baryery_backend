import logging

from src.bot.services import MessageSender
from src.core.db.db import get_session
from src.core.db.models import User
from src.core.db.repository import RequestRepository, UserRepository
from src.core.services.user_service import UserService


async def error_handler(sender: MessageSender, user: User, error: Exception) -> None:
    """Обработать ошибку отправки сообщения участнику.

    Если ошибка мессенджера означает, что пользователь заблокировал бота, отметить это
    в базе. Остальные ошибки только записываются в лог: недоставленное уведомление
    не должно ломать операцию администратора, которая уже сохранена в базе.
    """
    if not sender.is_blocking_error(error):
        logging.error(f"Сообщение пользователю {user} не отправлено: {error!r}", exc_info=error)
        return
    session_gen = get_session()
    session = await session_gen.asend(None)
    user_service = UserService(UserRepository(session), RequestRepository(session))
    await user_service.block_user(user)
    reason = str(error) or type(error).__name__
    logging.warning(f"Произведена блокировка пользователя: {user}. Причина блокировки: {reason}")
