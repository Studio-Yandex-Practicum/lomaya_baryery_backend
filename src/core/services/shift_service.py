import random
from datetime import date, timedelta
from itertools import cycle
from typing import Optional
from uuid import UUID

from fastapi import Depends
from telegram.ext import Application

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
from src.core.exceptions import (
    ObjectNotFoundError,
    ShiftCreateMultiplePreparingError,
    ShiftCreateRegistrationIsNotOverError,
    ShiftDateIntersectionError,
    ShiftDateMaxDurationError,
    ShiftDateStartFinishError,
    ShiftDateTodayPastError,
    ShiftDateUpdateStartError,
    ShiftUpdateError,
)
from src.core.services.task_service import TaskService
from src.core.settings import settings

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
        task_service: TaskService = Depends(),
    ) -> None:
        self.__shift_repository = shift_repository
        self.__task_service = task_service
        self.__telegram_bot = services.BotService

    def __check_date_not_today_or_in_past(self, date: date) -> None:
        """Проверка, что дата не является сегодняшним или прошедшим числом."""
        if date <= date.today():
            raise ShiftDateTodayPastError()

    def __check_started_and_finished_dates(self, started_at: date, finished_at: date) -> None:
        """Проверка дат начала и окончания смены между собой.

        - Дата начала не больше и не равна дате окончания.
        - Разница между датой начала и окончания не более 4-х месяцев.
        """
        if started_at >= finished_at:
            raise ShiftDateStartFinishError()
        if finished_at > (started_at + timedelta(days=120)):
            raise ShiftDateMaxDurationError()

    def __check_shifts_dates_intersection(self, preparing_started_at: date, started_finished_at: date) -> None:
        """Проверка наложения дат окончания текущей смены и начала новой смены."""
        if preparing_started_at <= started_finished_at:
            raise ShiftDateIntersectionError()

    def __check_that_request_filling_for_previous_shift_is_over(self, started_at: date) -> None:
        """Проверка, что приём заявок на участие в предыдущей смене закончен.

        Если текущая смена длится менее DAYS_FROM_START_OF_SHIFT_TO_JOIN дней (прием заявок не окончен),
        то создание новой смены запрещено. Параметр задается в настройках проекта.
        """
        if date.today() - started_at < timedelta(days=settings.DAYS_FROM_START_OF_SHIFT_TO_JOIN):
            raise ShiftCreateRegistrationIsNotOverError(amount_of_days=settings.DAYS_FROM_START_OF_SHIFT_TO_JOIN)

    def __check_that_request_filling_for_previous_shift_is_over(self, started_at: date) -> None:
        """Проверка, что приём заявок на участие в предыдущей смене закончен.

        Если текущая смена длится менее DAYS_FROM_START_OF_SHIFT_TO_JOIN дней (прием заявок не окончен),
        то создание новой смены запрещено. Параметр задается в настройках проекта.
        """
        if date.today() - started_at < timedelta(days=settings.DAYS_FROM_START_OF_SHIFT_TO_JOIN):
            raise CreateShiftForbiddenException(
                detail=f"Запрещено создавать новую смену, "
                f"если текущая смена запущена менее {settings.DAYS_FROM_START_OF_SHIFT_TO_JOIN} дней назад"
            )

    def __check_update_shift_forbidden(self, status: Shift.Status) -> None:
        """Проверка, что смену нельзя изменить.

        Нельзя изменять смены со статусами CANCELLED и FINISHED.
        """
        if status in (Shift.Status.CANCELLED, Shift.Status.FINISHED):
            raise ShiftUpdateError()

    def __check_shift_started_at_date_changed(self, started_at: date, update_started_at: date) -> None:
        """Проверка, что дата начала изменилась."""
        if started_at != update_started_at:
            raise ShiftDateUpdateStartError()

    async def __check_preparing_shift_already_exists(self) -> None:
        """Проверка, что новая смена уже существует.

        Если новая смена уже существует, то создание ещё одной запрещено.
        """
        if await self.__shift_repository.get_shift_with_status_or_none(Shift.Status.PREPARING):
            raise ShiftCreateMultiplePreparingError()

    async def __check_preparing_shift_dates(self, started_at: date, finished_at: date) -> None:
        """Проверка дат новой смены.

        - Если существует текущая смена, то проверяется был ли закончен прием заявок на участие.
        - Если прием заявок на текущую смену окончен, то сравниваются даты окончания текущей смены
        и начала новой смены. Иначе дата начала сравнивается с сегодняшним днем.
        - Сравниваются даты начала и окончания новой смены между собой.
        """
        started_shift = await self.__shift_repository.get_shift_with_status_or_none(Shift.Status.STARTED)
        if started_shift:
            self.__check_that_request_filling_for_previous_shift_is_over(started_shift.started_at)
            self.__check_shifts_dates_intersection(started_at, started_shift.finished_at)
        self.__check_date_not_today_or_in_past(started_at)
        self.__check_started_and_finished_dates(started_at, finished_at)

    async def __check_started_shift_dates(self, started_at: date, finished_at: date) -> None:
        """Проверка дат текущей смены.

        - Если существует новая смена, то сравниваются даты окончания текущей смены
        и начала новой смены.
        - Проверяется, что дата окончания не указана сегодняшним или вчерашним числом.
        - Сравниваются даты начала и окончания текущей смены между собой.
        """
        preparing_shift = await self.__shift_repository.get_shift_with_status_or_none(Shift.Status.PREPARING)
        if preparing_shift:
            self.__check_shifts_dates_intersection(preparing_shift.started_at, finished_at)
        self.__check_date_not_today_or_in_past(finished_at)
        self.__check_started_and_finished_dates(started_at, finished_at)

    async def __validate_shift_on_create(self, shift: Shift) -> None:
        """Валидация смены при создании."""
        await self.__check_preparing_shift_already_exists()
        await self.__check_preparing_shift_dates(shift.started_at, shift.finished_at)

    async def __validate_shift_on_update(self, shift: Shift, update_shift_data: ShiftUpdateRequest) -> None:
        """Валидация смены при обновлении."""
        self.__check_update_shift(shift.status)
        if shift.status == Shift.Status.STARTED:
            self.__check_shift_started_at_date_changed(shift.started_at, update_shift_data.started_at)
            await self.__check_started_shift_dates(update_shift_data.started_at, update_shift_data.finished_at)
        if shift.status == Shift.Status.PREPARING:
            await self.__check_preparing_shift_dates(update_shift_data.started_at, update_shift_data.finished_at)

    async def create_new_shift(self, new_shift: ShiftCreateRequest) -> Shift:
        shift = Shift(**new_shift.dict())
        await self.__validate_shift_on_create(shift)
        shift.status = Shift.Status.PREPARING
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
        await self.__validate_shift_on_update(shift, update_shift_data)
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

    async def finish_shift(self, bot: Application, id: UUID) -> Shift:
        shift = await self.__shift_repository.get_with_members(id, Member.Status.ACTIVE)
        await shift.finish()
        await self.__shift_repository.update(id, shift)
        await self.__telegram_bot(bot).notify_that_shift_is_finished(shift)
        return shift

    async def get_shift_with_members(self, id: UUID, member_status: Optional[Member.Status]) -> ShiftMembersResponse:
        shift = await self.__shift_repository.get_with_members(id, member_status)
        return ShiftMembersResponse(shift=shift, members=shift.members)

    async def list_all_requests(self, id: UUID, status: Optional[Request.Status]) -> list[ShiftDtoRespone]:
        shift_exists = await self.__shift_repository.check_shift_existence(id)
        if not shift_exists:
            raise ObjectNotFoundError(object_name=Shift.__name__, object_id=id)
        return await self.__shift_repository.list_all_requests(id=id, status=status)

    async def list_all_shifts(
        self, status: Optional[Shift.Status] = None, sort: Optional[ShiftSortRequest] = None
    ) -> list[ShiftWithTotalUsersResponse]:
        return await self.__shift_repository.get_shifts_with_total_users(status, sort)

    async def get_open_for_registration_shift_id(self) -> UUID:
        return await self.__shift_repository.get_open_for_registration_shift_id()
