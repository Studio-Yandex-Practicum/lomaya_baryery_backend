from dataclasses import dataclass
from datetime import date
from uuid import UUID

from src.core.db.models import Request, Shift, User


@dataclass
class FullReportDto:
    shift_id: UUID
    shift_status: Shift.Status
    shift_started_at: date
    report_id: UUID
    report_created_at: date
    user_name: str
    user_surname: str
    task_id: UUID
    task_description: str
    task_url: str
    photo_url: str


@dataclass
class TasksExcelReportDto:
    description: str
    approved: int
    declined: int
    waiting: int


@dataclass
class RequestDTO:
    request_id: UUID
    user_id: UUID
    name: str
    surname: str
    date_of_birth: date
    city: str
    phone_number: str
    request_status: Request.Status
    user_status: User.Status
