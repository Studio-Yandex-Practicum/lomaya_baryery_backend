import random
from datetime import date, timedelta
from itertools import cycle
from pathlib import Path
from typing import Optional
from uuid import UUID

from fastapi import Depends
from telegram.ext import Application

from src.api.request_models.shift import (
    ShiftCancelRequest,
    ShiftCreateRequest,
    ShiftSortRequest,
    ShiftUpdateRequest,
)
from src.api.response_models.shift import (
    ShiftDtoResponse,
    ShiftMembersResponse,
    ShiftWithTotalUsersResponse,
)
from src.bot import services
from src.core import exceptions
from src.core.db.models import Member, Report, Request, Shift, User
from src.core.db.repository import (
    ReportRepository,
    RequestRepository,
    ShiftRepository,
    UserRepository,
)
from src.core.services.task_service import TaskService
from src.core.settings import settings

FINAL_MESSAGE = (
    "Привет, {name} {surname}! "
    "Незаметно пролетели 3 месяца проекта. Мы рады, что ты принял участие и, надеемся, многому научился! "
    "В этой смене ты заработал {numbers_lombaryers} {lombaryers_case}. "
    "Ты можешь снова принять участие в проекте - регистрация на новый поток проекта будет доступна уже завтра!"
)

START_DATE_CHANGED_MESSAGE = "Дата старта смены изменилась. {started_at} в 08 часов утра тебе поступит первое задание."


class ShiftService:
    def __init__(
        self,
        shift_repository: ShiftRepository = Depends(),
        task_service: TaskService = Depends(),
        report_repository: ReportRepository = Depends(),
        user_repository: UserRepository = Depends(),
        request_repository: RequestRepository = Depends(),
    ) -> None:
        self.__shift_repository = shift_repository
        self.__task_service = task_service
        self.__report_repository = report_repository
        self.__user_repository = user_repository
        self.__request_repository = request_repository
        self.__telegram_bot = services.BotService

    def __check_date_not_today_or_in_past(self, _date: date) -> None:
        """Проверка, что дата не является сегодняшним или прошедшим числом."""
        if _date <= _date.today():
            raise exceptions.ShiftPastDateError

    def __check_started_and_finished_dates(self, started_at: date, finished_at: date) -> None:
        """Проверка дат начала и окончания смены между собой.

        - Дата начала не больше и не равна дате окончания.
        - Разница между датой начала и окончания не более 4-х месяцев.
        """
        if started_at >= finished_at:
            raise exceptions.ShiftTooShortError
        if finished_at > (started_at + timedelta(days=120)):
            raise exceptions.ShiftTooLongError

    def __check_shifts_dates_intersection(self, preparing_started_at: date, started_finished_at: date) -> None:
        """Проверка наложения дат окончания текущей смены и начала новой смены."""
        if preparing_started_at <= started_finished_at:
            raise exceptions.ShiftsDatesIntersectionError

    def __check_that_request_filling_for_previous_shift_is_over(self, started_at: date) -> None:
        """Проверка, что приём заявок на участие в предыдущей смене закончен.

        Если текущая смена длится менее DAYS_FROM_START_OF_SHIFT_TO_JOIN дней (прием заявок не окончен),
        то создание новой смены запрещено. Параметр задается в настройках проекта.
        """
        if date.today() - started_at < timedelta(days=settings.DAYS_FROM_START_OF_SHIFT_TO_JOIN):
            raise exceptions.ShiftCreatedTooFastError

    def __check_update_shift_forbidden(self, status: Shift.Status) -> None:
        """Проверка, что смену нельзя изменить.

        Нельзя изменять смены со статусами CANCELLED и FINISHED.
        """
        if status in (Shift.Status.CANCELLED, Shift.Status.FINISHED):
            raise exceptions.ChangeCompletedShiftError

    def __check_shift_started_at_date_changed(self, started_at: date, update_started_at: date) -> None:
        """Проверка, что дата начала изменилась."""
        if started_at != update_started_at:
            raise exceptions.CurrentShiftChangeDateError

    async def __check_preparing_shift_already_exists(self) -> None:
        """Проверка, что новая смена уже существует.

        Если новая смена уже существует, то создание ещё одной запрещено.
        """
        if await self.__shift_repository.get_shift_with_status_or_none(Shift.Status.PREPARING):
            raise exceptions.NewShiftExclusiveError

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
        else:
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
        self.__check_update_shift_forbidden(shift.status)
        if shift.status == Shift.Status.STARTED:
            self.__check_shift_started_at_date_changed(shift.started_at, update_shift_data.started_at)
            await self.__check_started_shift_dates(update_shift_data.started_at, update_shift_data.finished_at)
        if shift.status == Shift.Status.PREPARING:
            await self.__check_preparing_shift_dates(update_shift_data.started_at, update_shift_data.finished_at)

    async def __create_shift_dir(self, shift: Shift) -> None:
        shift_dir = await self.get_shift_dir(shift)
        path = Path(settings.USER_REPORTS_DIR / shift_dir)
        path.mkdir(parents=True, exist_ok=True)

    async def get_shift_dir(self, shift_id: UUID) -> str:
        shift = await self.__shift_repository.get(shift_id)
        return f"shift_{shift.sequence_number}"

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
        shift = await self.__shift_repository.create(instance=shift)
        await self.__create_shift_dir(shift.id)
        return shift

    async def get_shift(self, _id: UUID) -> Shift:
        return await self.__shift_repository.get(_id)

    async def update_shift(self, bot: Application, _id: UUID, update_shift_data: ShiftUpdateRequest) -> Shift:
        shift: Shift = await self.__shift_repository.get(_id)
        await self.__validate_shift_on_update(shift, update_shift_data)
        if shift.started_at != update_shift_data.started_at:
            shift.started_at = update_shift_data.started_at
            users = await self.__user_repository.get_users_by_shift_id(shift.id)
            await self.__telegram_bot(bot).notify_that_shift_start_date_is_changed(
                users,
                START_DATE_CHANGED_MESSAGE.format(
                    started_at=shift.started_at.strftime('%d.%m.%Y'),
                ),
            )

        shift.finished_at = update_shift_data.finished_at
        shift.title = update_shift_data.title
        shift.final_message = update_shift_data.final_message
        return await self.__shift_repository.update(_id, shift)

    async def start_shift(self, _id: UUID) -> Shift:
        shift = await self.__shift_repository.get(_id)
        await shift.start()
        await self.__shift_repository.update(_id, shift)
        return shift

    async def finish_shift(self, bot: Application, _id: UUID) -> Shift:
        shift = await self.__shift_repository.get_with_members(_id, Member.Status.ACTIVE)
        await shift.finish()
        await self.__shift_repository.update(_id, shift)
        await self.__telegram_bot(bot).notify_that_shift_is_finished(shift)
        return shift

    async def get_shift_with_members(self, _id: UUID, member_status: Optional[Member.Status]) -> ShiftMembersResponse:
        shift = await self.__shift_repository.get_with_members(_id, member_status)
        return ShiftMembersResponse(members=shift.members)

    async def list_all_requests(self, _id: UUID, status: Optional[Request.Status]) -> list[ShiftDtoResponse]:
        shift_exists = await self.__shift_repository.check_shift_existence(_id)
        if not shift_exists:
            raise exceptions.ObjectNotFoundError(Shift, _id)
        return await self.__shift_repository.list_all_requests(id=_id, status=status)

    async def list_all_shifts(
        self, status: Optional[list[Shift.Status]] = None, sort: Optional[ShiftSortRequest] = None
    ) -> list[ShiftWithTotalUsersResponse]:
        return await self.__shift_repository.get_shifts_with_total_users(status, sort)

    async def get_open_for_registration_shift_id(self) -> UUID:
        return await self.__shift_repository.get_open_for_registration_shift_id()

    async def finish_shift_automatically(self, bot: Application) -> None:
        shift = await self.__shift_repository.get_active_or_complete_shift()
        if not shift:
            return
        if shift.status is Shift.Status.READY_FOR_COMPLETE:
            await self.__decline_reports_and_notify_users(shift.id, bot)
            shift.status = Shift.Status.FINISHED
            await self.__shift_repository.update(shift.id, shift)
        if shift.finished_at + timedelta(days=1) == date.today():
            await self.__notify_users_with_reviewed_reports(shift.id, bot)
            unreviewed_report_exists = await self.__shift_repository.is_unreviewed_report_exists(shift.id)
            shift.status = Shift.Status.READY_FOR_COMPLETE if unreviewed_report_exists else Shift.Status.FINISHED
            await self.__shift_repository.update(shift.id, shift)

    async def __notify_users_with_reviewed_reports(self, shift_id: UUID, bot: Application) -> None:
        """Уведомляет пользователей, у которых нет непроверенных отчетов, об окончании смены."""
        shift = await self.__shift_repository.get_with_members_with_reviewed_reports(shift_id)
        await self.__telegram_bot(bot).notify_that_shift_is_finished(shift)

    async def __decline_reports_and_notify_users(self, shift_id: UUID, bot: Application) -> None:
        """Отклоняет непроверенные задания, уведомляет пользователей об окончании смены."""
        shift = await self.__shift_repository.get_with_members_and_unreviewed_reports(shift_id)
        reports_for_update = []
        for member in shift.members:
            for report in member.reports:
                report.status = Report.Status.DECLINED
                reports_for_update.append(report)
        await self.__report_repository.update_all(reports_for_update)
        await self.__telegram_bot(bot).notify_that_shift_is_finished(shift)

    async def cancel_shift(
        self, bot: Application, _id: UUID, cancel_shift_data: Optional[ShiftCancelRequest] = None
    ) -> Shift:
        shift = await self.__shift_repository.get_shift_with_request(_id)
        final_message = "Смена отменена"
        if cancel_shift_data:
            final_message = cancel_shift_data.final_message
        await shift.cancel(final_message)
        await self.__shift_repository.update(_id, shift)
        requests_to_update = []
        for request in shift.requests:
            if request.status == Request.Status.PENDING:
                request.status = Request.Status.DECLINED.value
                requests_to_update.append(request)
        await self.__request_repository.update_all(requests_to_update)

        users = await self.__user_repository.get_users_by_shift_id(shift.id)
        users_to_update = []
        for user in users:
            if user.status == User.Status.PENDING:
                user.status = User.Status.DECLINED.value
                users_to_update.append(user)
        await self.__user_repository.update_all(users_to_update)
        await self.__telegram_bot(bot).notify_that_shift_is_cancelled(users, final_message)
        return shift

    async def start_prepared_shift(self) -> None:
        """Запускает смену, если смена имеет статус preparing и дата старта совпадает с текущим днём."""
        shift = await self.__shift_repository.get_preparing_shift_with_started_at_today()
        if shift:
            shift.status = Shift.Status.STARTED.value
            await self.__shift_repository.update(shift.id, shift)

    async def get_started_shift_or_none(self) -> Optional[Shift]:
        """Возвращает активную на данный момент смену или None."""
        return await self.__shift_repository.get_started_shift_or_none()
