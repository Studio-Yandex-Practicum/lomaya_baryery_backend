from src.core.db.repository import RequestRepository, UserRepository
from src.core.services.user_service import UserService


async def get_registration_service_callback(sessions):
    try:
        async for session in sessions:
            request_repository = RequestRepository(session)
            user_repository = UserRepository(session)
            registration_service = UserService(user_repository, request_repository)
            return registration_service
    except ValueError:
        return None
