from datetime import datetime
from uuid import UUID

from fastapi import Depends

from src.api.request_models.shift import ShiftCreateRequest
from src.api.response_models.shift import ShiftUsersResponse
from src.core.db.models import Shift
from src.core.db.repository import ShiftRepository
from src.core.services.user_task_service import UserTaskService


class ShiftService:
    def __init__(self, shift_repository: ShiftRepository = Depends()) -> None:
        self.shift_repository = shift_repository

    async def create_new_shift(self, new_shift: ShiftCreateRequest) -> Shift:
        shift = Shift(**new_shift.dict())
        shift.status = Shift.Status.PREPARING
        return await self.shift_repository.create(shift=shift)

    async def get_shift(self, id: UUID) -> Shift:
        return await self.shift_repository.get(id)

    async def update_shift(self, id: UUID, update_shift_data: ShiftCreateRequest) -> Shift:
        return await self.shift_repository.update(id=id, shift=Shift(**update_shift_data.dict()))

    async def get_users_list(self, id: UUID) -> ShiftUsersResponse:
        shift = await self.shift_repository.get_with_users(id)
        users = shift.users
        return ShiftUsersResponse(shift=shift, users=users)

    async def start_shift(self, id: UUID) -> Shift:
        shift = await self.shift_repository.get(id)
        if shift.status in (Shift.Status.STARTED.value, Shift.Status.FINISHED.value, Shift.Status.CANCELING.value):
            # TODO изменить на кастомное исключение
            raise Exception
        user_service = UserTaskService(self.shift_repository.session)
        await user_service.distribute_tasks_on_shift(id)

        # TODO добавить вызов метода рассылки участникам первого задания

        update_shift_dict = {
            "started_at": datetime.now(),
            "status": Shift.Status.STARTED.value,
        }
        return await self.shift_repository.update(id=id, shift=Shift(**update_shift_dict))
