from src.core.db.db import get_session
from src.core.db.repository import (
    RequestRepository,
    ShiftRepository,
    TaskRepository,
    UserRepository,
    UserTaskRepository,
)
from src.core.services.request_sevice import RequestService
from src.core.services.task_service import TaskService
from src.core.services.user_service import UserService
from src.core.services.user_task_service import UserTaskService


async def get_registration_service_callback(sessions) -> UserService | None:
    async for session in sessions:  # noqa
        request_repository = RequestRepository(session)
        user_repository = UserRepository(session)
        registration_service = UserService(user_repository, request_repository)
        return registration_service


async def get_user_task_service_callback():
    async for session in get_session():
        request_repository = RequestRepository(session)
        shift_repository = ShiftRepository(session)
        task_repository = TaskRepository(session)
        user_repository = UserRepository(session)
        user_task_repository = UserTaskRepository(session)
        request_service = RequestService(request_repository)
        task_service = TaskService(task_repository)
        user_task_service = UserTaskService(
            user_task_repository,
            task_repository,
            shift_repository,
            task_service,
            request_service,
            request_repository,
            user_repository,
        )
    return user_task_service
