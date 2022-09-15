import uuid

from sqlalchemy import func, Column, TIMESTAMP, DATE, String, types
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """Базовая модель."""
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
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
