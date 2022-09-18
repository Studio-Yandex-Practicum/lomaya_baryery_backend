import uuid

from sqlalchemy import DATE, TIMESTAMP, Boolean, Column, String, func, types
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """Базовая модель."""
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    deleted = Column(Boolean, default=0)
    created_date = Column(
        TIMESTAMP, server_default=func.current_timestamp(), nullable=False
    )
    updated_date = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        onupdate=func.current_timestamp()
    )
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Shift(Base):
    """Смена."""
    status_choices = ENUM(
        "started", "finished", "preparing", "cancelled", name="status_choice"
    )
    status = Column(status_choices, nullable=False)
    started_at = Column(
        DATE, server_default=func.current_timestamp(), nullable=False
    )
    finished_at = Column(
        DATE, server_default=func.current_timestamp(), nullable=False
    )

    def __repr__(self):
        return f'<Shift: {self.id}, status: {self.status}>'


class Photo(Base):
    """Фотографии выполненных заданий."""
    url = Column(String(length=150), unique=True, nullable=False)

    def __repr__(self):
        return f'<Photo: {self.id}, url: {self.url}>'


class Task(Base):
    """Модель для описания задания."""
    url = Column(String(length=150), unique=True, nullable=False)
    description = Column(String(length=150), unique=True, nullable=False)

    def __repr__(self):
        return f'<Task: {self.id}, description: {self.description}>'
