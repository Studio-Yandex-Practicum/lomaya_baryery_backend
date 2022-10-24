from pydantic import BaseModel
from pydantic.schema import UUID


class ShortTaskResponse(BaseModel):
    """Схема для отображения task_id и task_url."""

    task_id: UUID
    task_url: str

    class Config:
        orm_mode = True


class TaskInfoResponse(ShortTaskResponse):
    """Схема для отображения информации о задании."""

    task_description: str
