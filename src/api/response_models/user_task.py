from pydantic import BaseModel
from pydantic.schema import UUID

from src.core.db.models import UserTask


class UserTaskResponse(BaseModel):
    """Pydantic-схема, для описания объекта, полученного из БД."""

    user_id: UUID
    id: UUID
    task_id: UUID
    day_number: int
    status: UserTask.Status
    # photo_url: str

    class Config:
        orm_mode = True
