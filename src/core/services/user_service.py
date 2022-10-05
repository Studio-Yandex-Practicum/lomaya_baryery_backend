from fastapi import Depends

from src.core.db.models import User
from src.core.db.repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository = Depends()) -> None:
        self.user_repository = user_repository

    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
        return await self.user_repository.get_by_telegram_id(telegram_id)
