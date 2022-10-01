from typing import Union
from uuid import UUID

from fastapi import Depends

from src.core.db.repository.shift_repository import ShiftRepository
from src.core.db.repository.user_repository import UserRepository


class UserService:
    def __init__(
        self, shift_repository: ShiftRepository = Depends(), user_repository: UserRepository = Depends()
    ) -> None:
        self.shift_repository = shift_repository
        self.user_repository = user_repository

    async def get_user_list_by_shift_id(self, shift_id: UUID) -> dict[str, Union[dict, list]]:
        """Получаем смену и список пользователей зарегистрированных на смену по shift_id."""
        shift = await self.shift_repository.get(
            shift_id,
        )
        users = await self.user_repository.get_user_list_by_shift_id(shift_id)
        return {"shift": shift, "users": users}
