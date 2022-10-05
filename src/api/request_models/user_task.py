from pydantic import Field, validator

from src.api.request_models.request_base import RequestBase
from src.core.db.models import UserTask


class ChangeStatusRequest(RequestBase):
    """Модель изменения статуса."""

    status: UserTask.Status = Field(UserTask.Status.APPROVED.value)

    @validator("status")
    def validate_status_allowed(cls, value: UserTask.Status) -> UserTask.Status:
        if value not in (UserTask.Status.APPROVED.value, UserTask.Status.DECLINED.value):
            raise ValueError("Недопустимый статус отчета")
        return value
