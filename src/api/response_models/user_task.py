from datetime import date

from pydantic import BaseModel
from pydantic.schema import UUID

from src.api.response_models.shift import ShiftResponse
from src.api.response_models.task import TaskInfoResponse
from src.api.response_models.user import UserInfoResponse
from src.core.db.models import UserTask


class UserAndTaskInfoResponse(UserInfoResponse, TaskInfoResponse):
    """Модель для ответа с обобщенной информацией о задании и юзере."""

    id: UUID


class UserTasksAndShiftResponse(BaseModel):
    """Общая модель смены и заданий для ответа."""

    shift: ShiftResponse
    tasks: list[UserAndTaskInfoResponse]


class UserTaskResponse(BaseModel):
    """Pydantic-схема, для описания объекта, полученного из БД."""

    user_id: UUID
    id: UUID
    task_id: UUID
    task_date: date
    status: UserTask.Status
    photo_url: str

    class Config:
        orm_mode = True


class UserTaskStatusByShiftResponse(BaseModel):
    shift_id: UUID
    shift_status: str
    shift_started_at: date
    user_task_id: UUID
    user_task_created_at: date
    user_name: str
    user_surname: str
    task_id: UUID
    task_description: str
    task_url: str
    photo_url: str

    class Config:
        orm_mode = True
