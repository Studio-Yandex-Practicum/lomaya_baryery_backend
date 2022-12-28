from dataclasses import dataclass
from datetime import date
from uuid import UUID

from src.core.db.models import Shift


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
class ShiftByUserWithReportSummaryDto:
    id: UUID
    title: str
    started_at: date
    finished_at: date
    numbers_lombaryers: int
    total_approved: int
    total_declined: int
    total_skipped: int
