from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel
from pydantic.schema import UUID

from src.core.db.models import Report, Shift


class ReportResponse(BaseModel):
    """Pydantic-схема, для описания объекта, полученного из БД."""

    shift_id: UUID
    task_id: UUID
    member_id: UUID
    updated_by: Optional[UUID]
    reviewed_at: Optional[datetime]
    task_date: date
    status: Report.Status
    report_url: Optional[str]
    uploaded_at: Optional[datetime]
    number_attempt: int

    class Config:
        orm_mode = True


class ReportSummaryResponse(BaseModel):
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
    photo_url: Optional[str]

    class Config:
        orm_mode = True


class ShortReportResponse(BaseModel):
    """Модель с краткой информацией об отчёте."""

    task_id: UUID
    task_date: date
    status: Report.Status

    class Config:
        orm_mode = True
