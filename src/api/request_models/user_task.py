from enum import Enum

from src.core.db.models import UserTask


class AllowedUserTaskStatus(str, Enum):
    """Допустимые статусы отчета участника."""

    APPROVED = UserTask.Status.APPROVED.value
    DECLINED = UserTask.Status.DECLINED.value
