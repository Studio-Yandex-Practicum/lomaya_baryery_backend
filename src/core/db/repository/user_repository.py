from typing import Optional

from sqlalchemy import exists, or_, select

from src.core.db.models import User
from src.core.db.repository import AbstractRepository


class UserRepository(AbstractRepository):
    """Репозиторий для работы с моделью User."""

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        user = await self.__session.execute(select(User).where(telegram_id == telegram_id))
        return user.scalars().first()

    async def check_user_existence(self, telegram_id: int, phone_number: str) -> bool:
        user_exists = await self.__session.execute(
            exists().where(or_(User.phone_number == phone_number, User.telegram_id == telegram_id))
        )
        return user_exists.scalar()


user_repository = UserRepository(User)
