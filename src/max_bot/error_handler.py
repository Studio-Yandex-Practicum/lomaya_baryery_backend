import logging

from aiomax.exceptions import AccessDeniedException, AiomaxException, ChatNotFound

from src.core.db.db import get_session
from src.core.db.models import User
from src.core.db.repository import RequestRepository, UserRepository
from src.core.services.user_service import UserService

# Ошибки API Max, означающие, что диалог с пользователем недоступен (бот остановлен/заблокирован)
ERRORS_TO_HANDLE = (AccessDeniedException, ChatNotFound)


async def error_handler(user: User, error: AiomaxException) -> None:
    if isinstance(error, ERRORS_TO_HANDLE):
        session_gen = get_session()
        session = await session_gen.asend(None)
        user_service = UserService(UserRepository(session), RequestRepository(session))
        await user_service.set_max_blocked(user)
        logging.warning(f"Произведена блокировка пользователя Max: {user}. Причина блокировки: {error}")
    else:
        raise error
