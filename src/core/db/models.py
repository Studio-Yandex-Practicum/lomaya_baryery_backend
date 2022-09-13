from datetime import datetime

from sqlmodel import SQLModel, Field


class BaseModel(SQLModel):
    """Базовая модель."""
    id: int = Field(primary_key=True, nullable=False)
    updated_at: datetime = Field(default=datetime.utcnow())
    created_at: datetime = Field(default=datetime.utcnow())


class Shift(BaseModel, table=True):
    """Смена."""
    started_at: datetime
    finished_at: datetime
