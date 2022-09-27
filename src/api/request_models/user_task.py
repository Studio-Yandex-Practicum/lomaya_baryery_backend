from enum import Enum

from src.core.db.models import UserTask


class AllowedUserTaskStatus(str, Enum):
    """Допустимые статусы отчета пользователя."""

    APPROVED = UserTask.Status.APPROVED
    DECLINED = UserTask.Status.DECLINED
