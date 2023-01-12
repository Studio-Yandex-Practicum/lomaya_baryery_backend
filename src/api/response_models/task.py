from pydantic import BaseModel
from pydantic.schema import UUID


class TaskInfoResponse(BaseModel):
    """Схема для отображения информации о задании с другими данными."""

    task_id: UUID
    task_url: str
    task_description: str


class TaskResponse(BaseModel):
    """Схема для отображения информации о задании."""

    id: UUID
    url: str
    description: str

    class Config:
        orm_mode = True
