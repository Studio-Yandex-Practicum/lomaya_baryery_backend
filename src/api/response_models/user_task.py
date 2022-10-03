<<<<<<< HEAD
from pydantic import BaseModel
from pydantic.schema import UUID

from src.api.response_models.shift import ShiftResponse
from src.core.db.models import UserTask
=======
from typing import List

from pydantic import BaseModel
from pydantic.schema import UUID

from src.core.db.models import UserTask

from .shift import ShiftResponseModel
from .task import TaskResponseModel
>>>>>>> eb7b34535d8035ebdbb4d7b2779231e5b5b30004


class UserAndTaskInfoResponseModel(BaseModel):
    """Модель для ответа c обобщенной информацией о задании и юзере."""

    id: UUID
    name: str
    surname: str
    task_id: UUID
    task_description: str
    task_url: str


class UserTaskResponseModel(BaseModel):
    """Общая модель смены и заданий для ответа."""

    shift: ShiftResponse
    tasks: list[UserAndTaskInfoResponseModel]


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
