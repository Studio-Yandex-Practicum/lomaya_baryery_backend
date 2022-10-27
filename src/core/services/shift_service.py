from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import Depends

from src.api.request_models.shift import ShiftCreateRequest
from src.api.response_models.shift import (
    ShiftDtoRespone,
    ShiftsResponse,
    ShiftUsersResponse,
)
from src.core.db.models import Request, Shift
from src.core.db.repository import ShiftRepository
from src.core.services.user_task_service import UserTaskService


class ShiftService:
    def __init__(
        self,
        shift_repository: ShiftRepository = Depends(),
        user_task_service: UserTaskService = Depends(),
    ) -> None:
        self.__shift_repository = shift_repository
        self.__user_task_service = user_task_service

    async def create_new_shift(self, new_shift: ShiftCreateRequest) -> Shift:
        shift = Shift(**new_shift.dict())
        shift.status = Shift.Status.PREPARING
        return await self.__shift_repository.create(shift=shift)

    async def get_shift(self, id: UUID) -> Shift:
        return await self.__shift_repository.get(id)

    async def update_shift(self, id: UUID, update_shift_data: ShiftCreateRequest) -> Shift:
        return await self.__shift_repository.update(id=id, shift=Shift(**update_shift_data.dict()))

    async def start_shift(self, id: UUID) -> Shift:
        shift = await self.__shift_repository.get(id)
        if shift.status in (Shift.Status.STARTED.value, Shift.Status.FINISHED.value, Shift.Status.CANCELING.value):
            # TODO изменить на кастомное исключение
            raise Exception
        await self.__user_task_service.distribute_tasks_on_shift(id)

        # TODO добавить вызов метода рассылки участникам первого задания

        update_shift_dict = {
            "started_at": datetime.now(),
            "status": Shift.Status.STARTED.value,
        }
        return await self.__shift_repository.update(id=id, shift=Shift(**update_shift_dict))

    async def get_users_list(self, id: UUID) -> ShiftUsersResponse:
        shift = await self.__shift_repository.get_with_users(id)
        users = shift.users
        return ShiftUsersResponse(shift=shift, users=users)

    async def list_all_requests(self, id: UUID, status: Optional[Request.Status]) -> list[ShiftDtoRespone]:
        return await self.__shift_repository.list_all_requests(id=id, status=status)

    async def list_all_shifts(self, status: Optional[Shift.Status], sort: Optional[Shift.Sort]) -> list[ShiftsResponse]:
        return await self.__shift_repository.get_shifts_with_status(status=status, sort=sort)
