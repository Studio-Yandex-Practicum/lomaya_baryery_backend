from typing import List

from pydantic import BaseModel
from pydantic.schema import UUID

from src.core.db.models import UserTask

from .shift import ShiftResponseModel
from .task import TaskResponseModel


class UserTaskResponseModel(BaseModel):
    """Общая модель смены и заданий для ответа."""

    shift: ShiftResponseModel
    tasks: List[TaskResponseModel]


class UserTaskDB(BaseModel):
    """Pydantic-схема, для описания объекта, полученного из БД."""

    user_task_id: UUID
    task_id: UUID
    day_number: int
    status: UserTask.Status
    photo_url: str

    class Config:
        orm_mode = True
