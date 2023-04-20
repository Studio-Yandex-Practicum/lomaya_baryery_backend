from pydantic import BaseModel
from pydantic.schema import UUID


class TaskResponse(BaseModel):
    """Схема для отображения информации о задании."""

    id: UUID
    url: str
    description: str
    description_for_message: str
    is_archived: bool

    class Config:
        orm_mode = True
