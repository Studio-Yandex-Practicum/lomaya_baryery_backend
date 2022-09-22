from datetime import date
from typing import List

from pydantic import BaseModel


class ShiftResponseModel(BaseModel):
    """Модель смены для ответа."""

    id: int
    status: str
    started_at: date
    finished_at: date


class TaskResponseModel(BaseModel):
    """Модель задания для ответа."""

    id: int
    name: str
    surname: str
    task_id: int
    task_description: str
    task_url: str


class UserTasksResponseModel(BaseModel):
    """Общая модель смены и заданий для ответа."""

    shift: ShiftResponseModel
    tasks: List[TaskResponseModel]
