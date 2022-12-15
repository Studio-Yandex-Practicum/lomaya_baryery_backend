from __future__ import annotations

from datetime import date

from pydantic import BaseModel
from pydantic.schema import UUID

from src.api.response_models.shift import ShiftResponse
from src.api.response_models.task import TaskInfoResponse
from src.api.response_models.user import UserInfoResponse
from src.core.db.models import Report, Shift


class UserAndTaskInfoResponse(UserInfoResponse, TaskInfoResponse):
    """Модель для ответа с обобщенной информацией о задании и юзере."""

    id: UUID


class ReportsAndShiftResponse(BaseModel):
    """Общая модель смены и заданий для ответа."""

    shift: ShiftResponse
    tasks: list[UserAndTaskInfoResponse]


class ReportResponse(BaseModel):
    """Pydantic-схема, для описания объекта, полученного из БД."""

    user_id: UUID
    id: UUID
    task_id: UUID
    task_date: date
    status: Report.Status
    photo_url: str

    class Config:
        orm_mode = True

    @classmethod
    def parse_from(cls, report_obj: Report) -> ReportResponse:
        """
        Парсинг данных из модели Report.

        Модель формируется в методе get_report_with_report_url класса ReportRepository.
        """
        return cls(
            user_id=report_obj.member.user_id,
            id=report_obj.id,
            task_id=report_obj.task_id,
            task_date=report_obj.task_date,
            status=report_obj.status,
            photo_url=report_obj.report_url,
        )


class ReportSummaryResponse(BaseModel):
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

    class Config:
        orm_mode = True
