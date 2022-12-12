import random
from datetime import date, timedelta
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
from src.bot import services
from src.core.db.models import Request, Shift
from src.core.db.repository import ShiftRepository
from src.core.exceptions import ShiftUpdateException
from src.core.services.report_service import ReportService
from src.core.services.task_service import TaskService

FINAL_MESSAGE = (
    "Привет, {name} {surname}! "
    "Незаметно пролетели 3 месяца проекта. Мы рады, что ты принял участие и, надеемся, многому научился! "
    "В этой смене ты заработал {numbers_lombaryers} ломбарьерчиков. "
    "Ты можешь снова принять участие в проекте - регистрация на новый поток проекта будет доступна уже завтра!"
)


class ShiftService:
    def __init__(
        self,
        shift_repository: ShiftRepository = Depends(),
        report_service: ReportService = Depends(),
        task_service: TaskService = Depends(),
    ) -> None:
        self.__shift_repository = shift_repository
        self.__report_service = report_service
        self.__task_service = task_service
        self.__telegram_bot = services.BotService

    def check_date_not_in_past(self, date: date) -> None:
        if date < date.today():
            raise ShiftUpdateException(detail="Нельзя установить дату начала/окончания смены прошедшим числом")

    def check_started_and_finished_dates(self, started_at: date, finished_at: date) -> None:
        if started_at >= finished_at:
            raise ShiftUpdateException(detail="Дата начала смены не может быть позже или равняться дате окончания")
        if finished_at > (date.today() + timedelta(days=120)):
            raise ShiftUpdateException(detail="Дата окончания не может быть больше 4-х месяцев")

    async def create_new_shift(self, new_shift: ShiftCreateRequest) -> Shift:
        shift = Shift(**new_shift.dict())
        self.check_date_not_in_past(shift.started_at)
        self.check_date_not_in_past(shift.finished_at)
        self.check_started_and_finished_dates(shift.started_at, shift.finished_at)
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
        shift: Shift = await self.__shift_repository.get(id)
        if shift.status in (Shift.Status.CANCELLED, Shift.Status.FINISHED):
            raise ShiftUpdateException(detail="Нельзя изменить завершенную или отмененную смену")
        if shift.status == Shift.Status.STARTED:
            if shift.started_at != update_shift_data.started_at:
                raise ShiftUpdateException(detail="Нельзя изменить дату начала текущей смены")
            self.check_date_not_in_past(update_shift_data.finished_at)
        if shift.status == Shift.Status.PREPARING:
            self.check_date_not_in_past(update_shift_data.started_at)
            self.check_date_not_in_past(update_shift_data.finished_at)
            self.check_started_and_finished_dates(update_shift_data.started_at, update_shift_data.finished_at)
        shift.started_at = update_shift_data.started_at
        shift.finished_at = update_shift_data.finished_at
        shift.title = update_shift_data.title
        shift.final_message = update_shift_data.final_message
        return await self.__shift_repository.update(id, shift)

    async def start_shift(self, id: UUID) -> Shift:
        shift = await self.__shift_repository.get(id)
        await shift.start()
        await self.__shift_repository.update(id, shift)
        return shift

    async def finish_shift(self, bot, id: UUID) -> Shift:
        shift = await self.__shift_repository.get_with_users(id)
        await shift.finish()
        await self.__shift_repository.update(id, shift)
        for user in shift.users:
            await self.__telegram_bot(bot).notify_that_shift_is_finished(user, shift.final_message)
        return shift

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
