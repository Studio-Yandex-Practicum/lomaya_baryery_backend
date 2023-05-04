from pydantic import BaseModel
from pydantic.schema import UUID


class TaskResponse(BaseModel):
    """Схема для отображения информации о задании."""

    id: UUID
    url: str
    title: str
    is_archived: bool
    sequence_number: int

    class Config:
        orm_mode = True
