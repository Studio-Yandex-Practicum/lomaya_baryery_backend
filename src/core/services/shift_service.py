from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import Depends

from src.api.request_models.shift import ShiftCreateRequest, ShiftSortRequest
from src.api.response_models.shift import (
    ShiftDtoRespone,
    ShiftUsersResponse,
    ShiftWithTotalUsersResponse,
)
from src.core.db.models import Request, Shift
from src.core.db.repository import ShiftRepository
from src.core.exceptions import NotFoundException
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
        # -----
        # Сейчас, чтобы смена создалась нужно добавить эти два поля вручную,
        # т.к. они являются обязательными в модели Shift и при этом
        # нигде ранее не задаются. Надо придумать, где они будут задаваться, кем и когда.
        # Проверял локально - помогает.

        # shift.title = 'title'
        # shift.final_message = 'final_message'

        # -----
        return await self.__shift_repository.create(instance=shift)

    async def get_shift(self, id: UUID) -> Shift:
        return await self.__shift_repository.get(id)

    async def update_shift(self, id: UUID, update_shift_data: ShiftCreateRequest) -> Shift:
        return await self.__shift_repository.update(id=id, instance=Shift(**update_shift_data.dict()))

    async def start_shift(self, id: UUID) -> Shift:
        shift = await self.__shift_repository.get(id)
        if shift.status in (Shift.Status.STARTED.value, Shift.Status.FINISHED.value, Shift.Status.CANCELING.value):
            raise NotFoundException(object_name=Shift.__doc__, object_id=id)
        # -----
        # Здесь запуск функции распределения заданий будет использовать
        # значение объекта смены started_at, указанное при создании(!) смены.
        # Ниже в словаре update_shift_dict задается новое значение
        # которое при запуске(!) смены окажется другим (может даже значительно).
        # Надо продумать этот момент с датами создания/запуска смены и,
        # соответственно её окончания.
        await self.__user_task_service.distribute_tasks_on_shift(id)
        # -----

        # TODO добавить вызов метода рассылки участникам первого задания

        update_shift_dict = {
            "started_at": datetime.now(),
            # -----
            # Без finished_at валидация для pydantic модели ShiftResponse не проходит:
            # pydantic.error_wrappers.ValidationError: 1 validation errors for ShiftResponse
            # response -> finished_at
            # none is not an allowed value (type=type_error.none.not_allowed)"
            # Для проверки ставил значение окончания смены заданное при ее создании. Помогло,
            # но в связи с вышеописанной проблемой возможно должно вычисляться по другому.
            # "finished_at": shift.finished_at,
            # -----
            "status": Shift.Status.STARTED.value,
        }
        return await self.__shift_repository.update(id=id, instance=Shift(**update_shift_dict))

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
