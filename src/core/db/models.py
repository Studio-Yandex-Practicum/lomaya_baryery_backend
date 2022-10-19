import enum
import uuid

from sqlalchemy import (
    DATE,
    TIMESTAMP,
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Enum,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey


@as_declarative()
class Base:
    """Базовая модель."""

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deleted = Column(Boolean, default=0)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(
        TIMESTAMP, server_default=func.current_timestamp(), nullable=False, onupdate=func.current_timestamp()
    )
    __name__: str


class Shift(Base):
    """Смена."""

    class Status(str, enum.Enum):
        """Статус смены."""

        STARTED = "started"
        FINISHED = "finished"
        PREPARING = "preparing"
        CANCELING = "cancelled"

    __tablename__ = "shifts"

    status = Column(
        Enum(Status, name="shift_status", values_callable=lambda obj: [e.value for e in obj]), nullable=False
    )
    started_at = Column(DATE, server_default=func.current_timestamp(), nullable=False, index=True)
    finished_at = Column(DATE, nullable=False, index=True)
    requests = relationship("Request", back_populates="shift")
    user_tasks = relationship("UserTask", back_populates="shift")
    users = relationship("Request", back_populates="shift")

    def __repr__(self):
        return f"<Shift: {self.id}, status: {self.status}>"


class Photo(Base):
    """Фотографии выполненных заданий."""

    __tablename__ = "photos"

    url = Column(String(length=150), unique=True, nullable=False)
    user_tasks = relationship("UserTask", back_populates="photo")

    def __repr__(self):
        return f"<Photo: {self.id}, url: {self.url}>"


class Task(Base):
    """Модель для описания задания."""

    __tablename__ = "tasks"

    url = Column(String(length=150), unique=True, nullable=False)
    description = Column(String(length=150), unique=True, nullable=False)
    user_tasks = relationship("UserTask", back_populates="task")

    def __repr__(self):
        return f"<Task: {self.id}, description: {self.description}>"


class User(Base):
    """Модель для пользователей."""

    __tablename__ = "users"

    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    date_of_birth = Column(DATE, nullable=False)
    city = Column(String(50), nullable=False)
    phone_number = Column(String(11), unique=True, nullable=False)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    requests = relationship("Request", back_populates="user")
    user_tasks = relationship("UserTask", back_populates="user")
    shifts = relationship("Request", back_populates="user")

    def __repr__(self):
        return f"<User: {self.id}, name: {self.name}, surname: {self.surname}>"


class Request(Base):
    """Модель рассмотрения заявок."""

    class Status(str, enum.Enum):
        """Статус рассмотрения заявки."""

        APPROVED = "approved"
        DECLINED = "declined"
        PENDING = "pending"
        REPEATED_REQUEST = "repeated request"

    __tablename__ = "requests"

    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id, ondelete="CASCADE"), nullable=False)
    shift_id = Column(UUID(as_uuid=True), ForeignKey(Shift.id), nullable=True)
    status = Column(
        Enum(Status, name="request_status", values_callable=lambda obj: [e.value for e in obj]), nullable=False
    )
    user = relationship("User", back_populates="requests")
    shift = relationship("Shift", back_populates="requests")

    def __repr__(self):
        return f"<Request: {self.id}, status: {self.status}>"


class UserTask(Base):
    """Ежедневные задания."""

    class Status(str, enum.Enum):
        """Статус задачи у пользователя."""

        NEW = "new"
        UNDER_REVIEW = "under_review"
        APPROVED = "approved"
        DECLINED = "declined"

    __tablename__ = "user_tasks"

    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id), nullable=False)
    shift_id = Column(UUID(as_uuid=True), ForeignKey(Shift.id), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey(Task.id), nullable=False)
    day_number = Column(Integer, CheckConstraint("day_number > 0 AND day_number < 100"))
    status = Column(
        Enum(Status, name="user_task_status", values_callable=lambda obj: [e.value for e in obj]), nullable=False
    )
    photo_id = Column(UUID(as_uuid=True), ForeignKey(Photo.id), nullable=True)
    user = relationship("User", back_populates="user_tasks")
    shift = relationship("Shift", back_populates="user_tasks")
    task = relationship("Task", back_populates="user_tasks")
    photo = relationship("Photo", back_populates="user_tasks")

    __table_args__ = (UniqueConstraint("user_id", "shift_id", "task_id", name="_user_task_uc"),)

    def __repr__(self):
        return f"<UserTask: {self.id}, day_number: {self.day_number}, " f"status: {self.status}>"
