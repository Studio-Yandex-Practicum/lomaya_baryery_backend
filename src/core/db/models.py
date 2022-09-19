import enum
import uuid

from sqlalchemy import (DATE, TIMESTAMP, Boolean, CheckConstraint, Column,
                        Enum, ForeignKey, Integer, String, UniqueConstraint,
                        func)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr


class UserTaskStatuses(str, enum.Enum):
    NEW = 'new'
    UNDER_REVIEW = 'under_review'
    APPROVED = 'approved'
    DECLINED = 'declined'


@as_declarative()
class Base:
    """Базовая модель."""
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    deleted = Column(
        Boolean,
        default=0
    )
    created_date = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False
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


class UserTask(Base):
    """Ежедневные задания."""
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('user.id'),
        nullable=False
    )
    shift_id = Column(
        UUID(as_uuid=True),
        ForeignKey('shift.id'),
        nullable=False
    )
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey('task.id'),
        nullable=False
    )
    day_number = Column(
        Integer,
        CheckConstraint('day_number > 0 AND day_number < 100')
    )
    status = Column(Enum(UserTaskStatuses))
    photo_id = Column(
        UUID(as_uuid=True),
        ForeignKey('photo.id'),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'shift_id',
            'task_id',
            name='_user_task_uc'
        )
    )

    def __repr__(self):
        return (f'<UserTask: {self.id}, day_number: {self.day_number}, '
                f'status: {self.status}>')
