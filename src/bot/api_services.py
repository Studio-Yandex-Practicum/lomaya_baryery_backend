from typing import Optional

from src.core.db.db import get_session
from src.core.db.repository import (
    MemberRepository,
    ReportRepository,
    RequestRepository,
    ShiftRepository,
    TaskRepository,
    UserRepository,
)
from src.core.services.report_service import ReportService
from src.core.services.request_sevice import RequestService
from src.core.services.user_service import UserService


async def get_registration_service_callback(sessions) -> Optional[UserService]:
    async for session in sessions:  # noqa
        request_repository = RequestRepository(session)
        user_repository = UserRepository(session)
        registration_service = UserService(user_repository, request_repository)
        return registration_service


async def get_report_service_callback():
    async for session in get_session():
        request_repository = RequestRepository(session)
        shift_repository = ShiftRepository(session)
        task_repository = TaskRepository(session)
        report_repository = ReportRepository(session)
        request_service = RequestService(request_repository)
        member_repository = MemberRepository(session)
        report_service = ReportService(
            report_repository,
            task_repository,
            shift_repository,
            request_service,
            member_repository,
        )
    return report_service
