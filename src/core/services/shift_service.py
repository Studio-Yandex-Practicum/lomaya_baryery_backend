import random
from datetime import datetime
from itertools import cycle
from typing import Optional
from uuid import UUID

from fastapi import Depends

from src.api.request_models.shift import (
    ShiftCreateRequest,
    ShiftSortRequest,
    ShiftUpdateRequest,
)
from src.api.response_models.shift import (
    ShiftDtoRespone,
    ShiftUsersResponse,
    ShiftWithTotalUsersResponse,
)
from src.core.db.models import Request, Shift
from src.core.db.repository import ShiftRepository
from src.core.exceptions import NotFoundException
from src.core.services.task_service import TaskService
from src.core.services.user_task_service import UserTaskService

FINAL_MESSAGE = (
    "Привет, {name} {surname}!"
    "Незаметно пролетели 3 месяца проекта. Мы рады, что ты принял участие и, надеемся, многому научился!"
    "В этой смене ты заработал {numbers_lombaryers} ломбарьерчиков."
    "Ты можешь снова принять участие в проекте - регистрация на новый поток проекта будет доступна уже завтра!"
)


class ShiftService:
    def __init__(
        self,
        shift_repository: ShiftRepository = Depends(),
        user_task_service: UserTaskService = Depends(),
        task_service: TaskService = Depends(),
    ) -> None:
        self.__shift_repository = shift_repository
        self.__user_task_service = user_task_service
        self.__task_service = task_service

    async def create_new_shift(self, new_shift: ShiftCreateRequest) -> Shift:
        shift = Shift(**new_shift.dict())
        shift.final_message = FINAL_MESSAGE
        shift.status = Shift.Status.PREPARING
        task_ids_list = list(map(str, await self.__task_service.get_task_ids_list()))
        random.shuffle(task_ids_list)
        month_tasks = {}
        for day, task_id in enumerate(cycle(task_ids_list), start=1):
            month_tasks[day] = task_id
            if day == 31:
                break
        shift.tasks = month_tasks
        return await self.__shift_repository.create(instance=shift)

    async def get_shift(self, id: UUID) -> Shift:
        return await self.__shift_repository.get(id)

    async def update_shift(self, id: UUID, update_shift_data: ShiftUpdateRequest) -> Shift:
        return await self.__shift_repository.update(id=id, instance=Shift(**update_shift_data.dict(exclude_unset=True)))

    async def start_shift(self, id: UUID) -> Shift:
        shift = await self.__shift_repository.get(id)
        if shift.status != Shift.Status.PREPARING.value:
            raise NotFoundException(object_name=Shift.__doc__, object_id=id)

        # TODO добавить вызов метода рассылки участникам первого задания

        update_shift_dict = {"started_at": datetime.now().date(), "status": Shift.Status.STARTED.value}
        updated_shift = await self.__shift_repository.update(id=id, instance=Shift(**update_shift_dict))
        return updated_shift  # noqa: R504

    async def get_users_list(self, id: UUID) -> ShiftUsersResponse:
        shift = await self.__shift_repository.get_with_users(id)
        users = shift.users
        return ShiftUsersResponse(shift=shift, users=users)

    async def list_all_requests(self, id: UUID, status: Optional[Request.Status]) -> list[ShiftDtoRespone]:
        return await self.__shift_repository.list_all_requests(id=id, status=status)

    async def list_all_shifts(
        self, status: Optional[Shift.Status], sort: Optional[ShiftSortRequest]
    ) -> list[ShiftWithTotalUsersResponse]:
        return await self.__shift_repository.get_shifts_with_total_users(status, sort)
