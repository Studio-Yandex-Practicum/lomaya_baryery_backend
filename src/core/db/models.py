import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DATE,
    JSON,
    TIMESTAMP,
    BigInteger,
    Boolean,
    Column,
    Enum,
    Identity,
    Integer,
    String,
    UniqueConstraint,
    func,
    select,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.schema import ForeignKey

from src.core import exceptions, settings


@as_declarative()
class Base:
    """Базовая модель."""

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        nullable=False,
        onupdate=func.current_timestamp(),
    )
    __name__: str


class Shift(Base):
    """Смена."""

    class Status(str, enum.Enum):
        """Статус смены."""

        STARTED = "started"
        FINISHED = "finished"
        READY_FOR_COMPLETE = "ready_for_complete"
        PREPARING = "preparing"
        CANCELLED = "cancelled"

    __tablename__ = "shifts"

    status = Column(
        Enum(Status, name="shift_status", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    sequence_number = Column(Integer, Identity(start=1, cycle=True))
    started_at = Column(DATE, server_default=func.current_timestamp(), nullable=False, index=True)
    finished_at = Column(DATE, nullable=False, index=True)
    title = Column(String(60), nullable=False)
    final_message = Column(String(400), nullable=False)
    tasks = Column(JSON, nullable=False)
    requests = relationship("Request", back_populates="shift")
    reports = relationship("Report", back_populates="shift")
    members = relationship("Member", back_populates="shift", order_by="Member.member_user_name")

    def __repr__(self):
        return f"<Shift: {self.id}, status: {self.status}>"

    async def start(self):
        if self.status != Shift.Status.PREPARING.value:
            raise exceptions.ShiftStartError(self)
        self.status = Shift.Status.STARTED.value
        self.started_at = datetime.now().date()

    async def finish(self):
        if self.status != Shift.Status.STARTED.value:
            raise exceptions.ShiftFinishError(self)
        self.status = Shift.Status.FINISHED.value
        self.finished_at = datetime.now().date()

    async def cancel(self, final_message: str):
        if self.status != Shift.Status.PREPARING.value:
            raise exceptions.ShiftCancelError(self)
        self.final_message = final_message
        self.status = Shift.Status.CANCELLED.value
        self.finished_at = datetime.now().date()


class Task(Base):
    """Модель для описания задания."""

    __tablename__ = "tasks"

    url = Column(String(length=150), unique=True, nullable=False)
    description = Column(String(length=150), unique=True, nullable=False)
    description_for_message = Column(String(length=150), unique=True, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    reports = relationship("Report", back_populates="task")

    def __repr__(self):
        return f"<Task: {self.id}, description: {self.description}>"


class User(Base):
    """Модель для пользователей."""

    class Status(str, enum.Enum):
        """Статус пользователя."""

        VERIFIED = "verified"
        DECLINED = "declined"
        PENDING = "pending"

    __tablename__ = "users"

    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    date_of_birth = Column(DATE, nullable=False)
    city = Column(String(50), nullable=False)
    phone_number = Column(String(16), unique=True, nullable=False)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    status = Column(
        Enum(Status, name="user_status", values_callable=lambda obj: [e.value for e in obj]),
        default=Status.PENDING.value,
        nullable=False,
    )
    requests = relationship("Request", back_populates="user")
    members = relationship("Member", back_populates="user")
    telegram_blocked = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<User: {self.id}, name: {self.name}, surname: {self.surname}>"


class Request(Base):
    """Модель рассмотрения заявок."""

    class Status(str, enum.Enum):
        """Статус рассмотрения заявки."""

        APPROVED = "approved"
        DECLINED = "declined"
        PENDING = "pending"

    __tablename__ = "requests"

    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id, ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="requests")
    shift_id = Column(UUID(as_uuid=True), ForeignKey(Shift.id), nullable=True)
    shift = relationship("Shift", back_populates="requests")
    status = Column(
        Enum(Status, name="request_status", values_callable=lambda obj: [e.value for e in obj]),
        default=Status.PENDING.value,
        nullable=False,
    )
    is_repeated = Column(Integer, default=1, nullable=False)

    def __repr__(self):
        return f"<Request: {self.id}, status: {self.status}>"


class Member(Base):
    """Модель участников смены."""

    class Status(str, enum.Enum):
        """Статус участника смены."""

        ACTIVE = "active"
        EXCLUDED = "excluded"

    __tablename__ = "members"

    status = Column(
        Enum(Status, name="member_status", values_callable=lambda obj: [e.value for e in obj]),
        default=Status.ACTIVE.value,
        nullable=False,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id), nullable=False)
    user = relationship("User", back_populates="members")
    shift_id = Column(UUID(as_uuid=True), ForeignKey(Shift.id), nullable=False)
    shift = relationship("Shift", back_populates="members")
    numbers_lombaryers = Column(Integer, default=0, nullable=False)
    reports = relationship("Report", back_populates="member", order_by='Report.task_date')
    member_user_name = deferred((select(User.name).where(User.id == user_id)).scalar_subquery())

    __table_args__ = (UniqueConstraint("user_id", "shift_id", name="_user_shift_uc"),)

    def __repr__(self):
        return f"<Member: {self.id}, status: {self.status}>"


class Administrator(Base):
    """Модель администратора смены."""

    class Status(str, enum.Enum):
        """Cтатус администратора."""

        ACTIVE = "active"
        BLOCKED = "blocked"

    class Role(str, enum.Enum):
        """Роль администратора."""

        ADMINISTRATOR = "administrator"
        PSYCHOLOGIST = "psychologist"

    __tablename__ = "administrators"

    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(70), nullable=False)
    role = Column(
        Enum(Role, name="administrator_role", values_callable=lambda obj: [e.value for e in obj]), nullable=False
    )
    last_login_at = Column(TIMESTAMP)
    status = Column(
        Enum(Status, name="administrator_status", values_callable=lambda obj: [e.value for e in obj]), nullable=False
    )
    reports = relationship("Report", back_populates="reviewer")
    is_superadmin = Column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<Administrator: {self.name} {self.surname}, role: {self.role}>"


class Report(Base):
    """Ежедневные задания."""

    class Status(str, enum.Enum):
        """Статус задачи у пользователя."""

        REVIEWING = "reviewing"
        APPROVED = "approved"
        DECLINED = "declined"
        WAITING = "waiting"
        SKIPPED = "skipped"
        NOT_PARTICIPATE = "not_participate"

    __tablename__ = "reports"

    shift_id = Column(UUID(as_uuid=True), ForeignKey(Shift.id), nullable=False)
    shift = relationship("Shift", back_populates="reports")
    task_id = Column(UUID(as_uuid=True), ForeignKey(Task.id), nullable=False)
    task = relationship("Task", back_populates="reports")
    member_id = Column(UUID(as_uuid=True), ForeignKey(Member.id), nullable=False)
    member = relationship("Member", back_populates="reports")
    updated_by = Column(UUID(as_uuid=True), ForeignKey(Administrator.id), nullable=True)
    reviewer = relationship("Administrator", back_populates="reports")
    reviewed_at = Column(TIMESTAMP, nullable=True)
    task_date = Column(DATE, nullable=False)
    status = Column(
        Enum(Status, name="report_status", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    report_url = Column(String(length=4096), unique=True, nullable=True)
    uploaded_at = Column(TIMESTAMP, nullable=True)
    number_attempt = Column(Integer, nullable=False, server_default='0')

    __table_args__ = (UniqueConstraint("shift_id", "task_date", "member_id", name="_member_task_uc"),)

    def __repr__(self):
        return f"<Report: {self.id}, task_date: {self.task_date}, status: {self.status}>"

    def send_report(self, photo_url: str):
        if self.number_attempt == settings.NUMBER_ATTEMPTS_SUBMIT_REPORT:
            raise exceptions.ExceededAttemptsReportError
        if not photo_url:
            raise exceptions.EmptyReportError
        if self.status not in (
            Report.Status.WAITING.value,
            Report.Status.DECLINED.value,
        ):
            raise exceptions.CannotAcceptReportError
        self.status = Report.Status.REVIEWING.value
        self.report_url = photo_url
        self.uploaded_at = datetime.now()
        self.number_attempt += 1

    def set_reviewer(self, administrator_id: UUID):
        """Установить администратора, который проверил отчет и дату проверки."""
        self.updated_by = administrator_id
        self.reviewed_at = datetime.now()


class AdministratorInvitation(Base):
    """Модель приглашения администратора/психолога."""

    __tablename__ = "administrator_invitations"

    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    token = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    expired_datetime = Column(TIMESTAMP, nullable=False)

    def __repr__(self) -> str:
        return f"<AdministratorInvitation: {self.id}, email: {self.email}, surname: {self.surname}, name: {self.name}>"
