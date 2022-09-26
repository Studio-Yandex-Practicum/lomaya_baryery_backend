from typing import List

from pydantic import BaseModel

from .shift import ShiftResponseModel
from .task import TaskResponseModel


class UserTaskResponseModel(BaseModel):
    """Общая модель смены и заданий для ответа."""

    shift: ShiftResponseModel
    tasks: List[TaskResponseModel]
