from telegram.error import BadRequest, Forbidden, TelegramError

from src.core.db.db import get_session
from src.core.db.models import User
from src.core.db.repository import RequestRepository, UserRepository
from src.core.services.user_service import UserService

ERRORS_TO_HANDLE = {
    BadRequest: ("Chat not found",),
    Forbidden: ("Forbidden: bot was blocked by the user",),
}


async def error_handler(user: User, error: TelegramError) -> None:
    error_type = type(error)
    if error_type in ERRORS_TO_HANDLE and error.message in ERRORS_TO_HANDLE[error_type]:
        session_gen = get_session()
        session = await session_gen.asend(None)
        user_service = UserService(UserRepository(session), RequestRepository(session))
        await user_service.set_telegram_blocked(user)
    else:
        raise error
