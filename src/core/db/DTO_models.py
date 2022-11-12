from dataclasses import dataclass
from datetime import date
from uuid import UUID

from src.core.db.models import Shift


@dataclass
class FullUserTaskDto():
    shift_id: UUID
    shift_status: Shift.Status
    shift_started_at: date
    user_task_id: UUID
    user_task_created_at: date
    user_name: str
    user_surname: str
    task_id: UUID
    task_description: str
    task_url: str
    photo_url: str
