from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from sqlalchemy.engine import Row

from src.core.db.models import Administrator, Report, Request, Shift, User


@dataclass
class AdministratorAndTokensDTO:
    access_token: str
    refresh_token: str
    administrator: Administrator


@dataclass
class FullReportDto:
    shift_id: UUID
    shift_status: Shift.Status
    shift_started_at: date
    report_id: UUID
    report_status: Report.Status
    report_created_at: date
    report_uploaded_at: datetime | None
    updated_by: UUID | None
    report_reviewed_at: datetime | None
    user_name: str
    user_surname: str
    task_id: UUID
    task_title: str
    task_url: str
    photo_url: str


@dataclass
class TasksAnalyticReportDto:
    sequence_number: int
    title: str
    approved: int
    declined: int
    skipped: int


@dataclass
class ShiftAnalyticReportDto:
    sequence_number: int
    title: str
    approved_from_1_attempt: int
    approved_from_2_attempt: int
    approved_from_3_attempt: int
    approved: int
    declined: int
    skipped: int
    reports_total: int


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

    @classmethod
    def parse_from_db(cls, db_row: Row):
        return RequestDTO(
            request_id=db_row.request_id,
            user_id=db_row.user_id,
            name=db_row.name,
            surname=db_row.surname,
            date_of_birth=db_row.date_of_birth,
            city=db_row.city,
            phone_number=db_row.phone_number,
            request_status=db_row.request_status,
            user_status=db_row.user_status,
        )


@dataclass
class ShiftByUserWithReportSummaryDto:
    id: UUID
    title: str
    started_at: date
    finished_at: date
    numbers_lombaryers: int
    member_id: UUID
    total_approved: int
    total_declined: int
    total_skipped: int
    is_excluded: bool


@dataclass
class UserAnalyticReportDto:
    sequence_number: int
    title: str
    approved_from_1_attempt: int
    approved_from_2_attempt: int
    approved_from_3_attempt: int
    approved: int
    declined: int
    skipped: int
    reports_total: int
