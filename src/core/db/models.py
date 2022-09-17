import re
import uuid

from sqlalchemy import func, Column, TIMESTAMP, DATE, String, INTEGER
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import validates
from sqlalchemy.schema import ForeignKey


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


class User(Base):
    """Модель для пользователей"""
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    date_of_birth = Column(DATE, nullable=False)
    address = Column(String(50), nullable=False)
    phone_number = Column(INTEGER, unique=True, nullable=False)

    def __repr__(self):
        return f'<User: {self.id}, name: {self.name}, surname: {self.surname}>'

    @validates('name', 'surname')
    def validate_name_and_surname(self, key, value) -> str:
        regex = "^[a-zа-яё ]+$"
        if re.compile(regex).search(value.lower()) is None:
            raise ValueError('Фамилия или имя не корректные')
        if len(value) < 2:
            raise ValueError('Фамилия и имя должны быть больше 2 символов')
        return value.upper()

    @validates('address')
    def validate_address(self, key, value) -> str:
        regex = "^[a-zA-Zа-яА-ЯёЁ -]+$"
        if re.compile(regex).search(value) is None:
            raise ValueError('Адресс не корректны')
        if len(value) < 2:
            raise ValueError('Адресс слишком короткий')
        return value

    @validates('phone_number')
    def validate_phone_number(self, key, value) -> str:
        if len(str(value)) == 11:
            raise ValueError('Поле телефона должно состоять из 11 цифр')
        return value


class Request(Base):
    """Модель рассмотрения заявок"""
    approved_choices = ENUM(
        "approved", "declined", "pending", name="approved_choices"
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    shift_id = Column(
        UUID(as_uuid=True), ForeignKey("shift.id"), nullable=False
    )
    approved = Column(approved_choices, nullable=False)

    def __repr__(self):
        return f'<Request: {self.id}, approved: {self.approved}>'
