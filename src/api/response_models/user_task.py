from pydantic import BaseModel
from pydantic.schema import UUID

from pydantic import BaseModel

from .shift import ShiftResponseModel
from .task import TaskResponseModel
from src.core.db.models import UserTask


class UserTaskResponseModel(BaseModel):
    """Общая модель смены и заданий для ответа."""

    shift: ShiftResponseModel
    tasks: list[TaskResponseModel]


class UserTaskResponse(BaseModel):
    """Pydantic-схема, для описания объекта, полученного из БД."""

    user_id: UUID
    user_task_id: UUID
    task_id: UUID
    day_number: int
    status: UserTask.Status
    photo_url: str

    class Config:
        orm_mode = True
