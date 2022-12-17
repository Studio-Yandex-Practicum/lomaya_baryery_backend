import random
from datetime import date, timedelta
from itertools import cycle
from typing import Optional
from uuid import UUID

from fastapi import BackgroundTasks, Depends

from src.api.request_models.shift import (
    ShiftCreateRequest,
    ShiftSortRequest,
    ShiftUpdateRequest,
)
from src.api.response_models.shift import (
    ShiftDtoRespone,
    ShiftMembersResponse,
    ShiftWithTotalUsersResponse,
)
from src.bot import services
from src.core.db.models import Member, Request, Shift
from src.core.db.repository import ShiftRepository
from src.core.exceptions import ShiftUpdateException, UpdateShiftForbiddenException
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

    def __check_date_not_in_past(self, date: date) -> None:
        """Проверка, что дата не является прошедшим числом."""
        if date < date.today():
            raise ShiftUpdateException(detail="Нельзя установить дату начала/окончания смены прошедшим числом")

    def __check_started_and_finished_dates(self, started_at: date, finished_at: date) -> None:
        """Проверка дат начала и окончания смены между собой.

        - Дата начала не больше и не равна дате окончания.
        - Разница между датой начала и окончания не более 4-х месяцев.
        """
        if started_at >= finished_at:
            raise ShiftUpdateException(detail="Дата начала смены не может быть позже или равняться дате окончания")
        if finished_at > (started_at + timedelta(days=120)):
            raise ShiftUpdateException(detail="Смена не может длиться больше 4-х месяцев")

    def __validate_shift(self, shift: Shift, update_shift_data: ShiftUpdateRequest = None) -> None:
        """Валидация смены в зависимости от её статуса.

        Если update_shift_data не передано в функцию (при создании смены),
        то проверяются даты самой смены.
        """
        if shift.status in (Shift.Status.CANCELLED, Shift.Status.FINISHED):
            raise UpdateShiftForbiddenException(detail="Нельзя изменить завершенную или отмененную смену")
        if shift.status == Shift.Status.STARTED:
            if shift.started_at != update_shift_data.started_at:
                raise UpdateShiftForbiddenException(detail="Нельзя изменить дату начала текущей смены")
            self.__check_date_not_in_past(update_shift_data.finished_at)
            self.__check_started_and_finished_dates(update_shift_data.started_at, update_shift_data.finished_at)
        if not update_shift_data:
            # Используется для передачи дат создаваемой смены в проверяющие функции,
            # т.к. объект update_shift_data при создании смены не передается в функцию.
            update_shift_data = shift
        if shift.status == Shift.Status.PREPARING:
            self.__check_date_not_in_past(update_shift_data.started_at)
            self.__check_date_not_in_past(update_shift_data.finished_at)
            self.__check_started_and_finished_dates(update_shift_data.started_at, update_shift_data.finished_at)

    async def create_new_shift(self, new_shift: ShiftCreateRequest) -> Shift:
        shift = Shift(**new_shift.dict())
        shift.status = Shift.Status.PREPARING
        self.__validate_shift(shift)
        shift.final_message = FINAL_MESSAGE
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
        self.__validate_shift(shift, update_shift_data)
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

    async def finish_shift(self, bot, id: UUID, background_tasks: BackgroundTasks) -> Shift:
        shift = await self.__shift_repository.get_with_members(id, Member.Status.ACTIVE)
        await shift.finish()
        await self.__shift_repository.update(id, shift)
        for member in shift.members:
            background_tasks.add_task(
                self.__telegram_bot(bot).notify_that_shift_is_finished, member, shift.final_message
            )
        return shift

    async def get_shift_with_members(self, id: UUID, member_status: Optional[Member.Status]) -> ShiftMembersResponse:
        shift = await self.__shift_repository.get_with_members(id, member_status)
        return ShiftMembersResponse(shift=shift, members=shift.members)

    async def list_all_requests(self, id: UUID, status: Optional[Request.Status]) -> list[ShiftDtoRespone]:
        return await self.__shift_repository.list_all_requests(id=id, status=status)

    async def list_all_shifts(
        self, status: Optional[Shift.Status], sort: Optional[ShiftSortRequest]
    ) -> list[ShiftWithTotalUsersResponse]:
        return await self.__shift_repository.get_shifts_with_total_users(status, sort)
