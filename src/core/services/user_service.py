from uuid import UUID

from fastapi import Depends

from src.api.response_models.shift import ShiftUsersResponse
from src.core.db.repository.shift_repository import ShiftRepository


class UserService:
    def __init__(
        self,
        shift_repository: ShiftRepository = Depends(),
    ) -> None:
        self.shift_repository = shift_repository

    async def get_user_list_by_shift_id(self, shift_id: UUID) -> ShiftUsersResponse:
        """Получаем смену и список пользователей зарегистрированных на смену по shift_id."""
        shift = await self.shift_repository.get(shift_id)
        users = await self.shift_repository.get_users(shift_id)
        return ShiftUsersResponse(shift=shift, users=users)
