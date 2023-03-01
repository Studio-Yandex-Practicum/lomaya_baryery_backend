from pydantic import BaseModel
from pydantic.schema import UUID


class TaskInfoResponse(BaseModel):
    """Схема для отображения информации о задании."""

    task_id: UUID
    task_url: str
    task_description: str
    task_description_for_message: str


class TaskResponse(BaseModel):
    """Схема для отображения информации о задании."""

    id: UUID
    url: str
    description: str
    description_for_message: str

    class Config:
        orm_mode = True
