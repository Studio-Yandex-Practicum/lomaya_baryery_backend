import uuid as uuid_pkg
from datetime import datetime

from sqlalchemy import func
from sqlmodel import SQLModel, Field


class MainBaseModel(SQLModel):
    """Базовая модель."""
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default=datetime.utcnow())


class Shift(MainBaseModel, table=True):
    """Смена."""
    started_at: datetime
    finished_at: datetime
