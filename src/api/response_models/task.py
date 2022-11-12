from pydantic import BaseModel
from pydantic.schema import UUID


class TaskInfoResponse(BaseModel):
    """Схема для отображения информации о задании."""

    task_id: UUID
    task_url: str
    task_description: str


class LongTaskResponse(TaskInfoResponse):
    """Схема для отображения информации о задании и адреса получателя."""

    user_telegram_id: int

    class Config:
        orm_mode = True
