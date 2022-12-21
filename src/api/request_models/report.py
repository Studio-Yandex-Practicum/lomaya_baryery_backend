from typing import Optional

from pydantic import Field, validator

from src.api.request_models.request_base import RequestBase
from src.core.db.models import Report


class ChangeStatusRequest(RequestBase):
    """Модель изменения статуса."""

    status: Report.Status = Field(Report.Status.APPROVED.value)

    @validator("status")
    def validate_status_allowed(cls, value: Report.Status) -> Report.Status:
        if value not in (Report.Status.APPROVED.value, Report.Status.DECLINED.value):
            raise ValueError("Недопустимый статус отчета")
        return value


class ReportUpdateRequest(RequestBase):
    status: Optional[Report.Status]
    report_url: Optional[str]
