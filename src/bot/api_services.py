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
from src.core.services.shift_service import ShiftService
from src.core.services.task_service import TaskService
from src.core.services.user_service import UserService


async def get_user_service_callback(sessions) -> Optional[UserService]:
    async for session in sessions:  # noqa R503
        task_repository = TaskRepository(session)
        shift_repository = ShiftRepository(session)
        task_service = TaskService(task_repository)
        request_repository = RequestRepository(session)
        user_repository = UserRepository(session)
        shift_service = ShiftService(shift_repository, task_service)
        user_service = UserService(user_repository, request_repository, shift_service)
        return user_service


async def get_report_service_callback(sessions):
    async for session in sessions:  # noqa R503
        shift_repository = ShiftRepository(session)
        task_repository = TaskRepository(session)
        report_repository = ReportRepository(session)
        member_repository = MemberRepository(session)
        task_service = TaskService(task_repository)
        member_service = MemberService(member_repository, shift_repository)
        report_service = ReportService(
            report_repository, shift_repository, member_repository, task_service, member_service
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
