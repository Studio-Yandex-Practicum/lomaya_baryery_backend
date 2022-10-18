from typing import Optional

from pydantic import BaseModel
from pydantic.schema import UUID


class TaskInfoResponse(BaseModel):
    """Схема для отображения информации о задании."""

    task_id: UUID
    task_description: str
    task_url: str


class ShortTaskResponse(TaskInfoResponse):
    """Схема для отображения task_id и task_url."""

    task_description: Optional[str]

    class Config:
        orm_mode = True
