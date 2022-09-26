from uuid import UUID

from pydantic import BaseModel


class TaskResponseModel(BaseModel):
    """Модель для ответа c обобщенной информацией о задании и юзере."""

    id: UUID
    name: str
    surname: str
    task_id: UUID
    task_description: str
    task_url: str
