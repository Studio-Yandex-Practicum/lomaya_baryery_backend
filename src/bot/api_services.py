from typing import Optional

from src.core.db.repository import (
    MemberRepository,
    ReportRepository,
    RequestRepository,
    ShiftRepository,
    TaskRepository,
    UserRepository,
)
from src.core.services.member_service import MemberService
from src.core.services.report_service import ReportService
from src.core.services.request_service import RequestService
from src.core.services.task_service import TaskService
from src.core.services.user_service import UserService


async def get_registration_service_callback(sessions) -> Optional[UserService]:
    async for session in sessions:  # noqa R503
        request_repository = RequestRepository(session)
        user_repository = UserRepository(session)
        registration_service = UserService(user_repository, request_repository)
        return registration_service


async def get_report_service_callback(sessions):
    async for session in sessions:  # noqa R503
        request_repository = RequestRepository(session)
        shift_repository = ShiftRepository(session)
        task_repository = TaskRepository(session)
        report_repository = ReportRepository(session)
        member_repository = MemberRepository(session)
        request_service = RequestService(request_repository, member_repository)
        task_service = TaskService(task_repository)
        report_service = ReportService(
            report_repository, task_repository, shift_repository, member_repository, request_service, task_service
        )
        return report_service


async def get_member_service_callback(sessions):
    async for session in sessions:  # noqa R503
        member_repository = MemberRepository(session)
        shift_repository = ShiftRepository(session)
        member_service = MemberService(
            member_repository, shift_repository
        )
        return member_service
