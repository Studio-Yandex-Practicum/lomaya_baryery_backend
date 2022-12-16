from __future__ import annotations

from datetime import date

from pydantic import BaseModel
from pydantic.schema import UUID

from src.api.response_models.task import TaskInfoResponse
from src.api.response_models.user import UserInfoResponse
from src.core.db.models import Report, Shift


class UserAndTaskInfoResponse(UserInfoResponse, TaskInfoResponse):
    """Модель для ответа с обобщенной информацией о задании и юзере."""

    id: UUID


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
    def parse_from(cls, obj: Report) -> ReportResponse:
        """
        Парсинг данных из модели Report.

        Модель формируется в методе get_report_with_report_url класса ReportRepository.
        """
        return cls(
            user_id=obj.member.user_id,
            id=obj.id,
            task_id=obj.task_id,
            task_date=obj.task_date,
            status=obj.status,
            photo_url=obj.report_url,
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
