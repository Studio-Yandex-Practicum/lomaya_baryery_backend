from dataclasses import astuple
from datetime import date
from io import BytesIO
from urllib.parse import quote_plus
from uuid import UUID

from fastapi import Depends
from openpyxl import Workbook

from src.core.db.repository.shift_repository import ShiftRepository
from src.core.db.repository.task_repository import TaskRepository
from src.core.db.repository.user_repository import UserRepository
from src.excel_generator.builder import AnalyticReportBuilder
from src.excel_generator.shift_builder import ShiftAnalyticReportSettings
from src.excel_generator.task_builder import TaskAnalyticReportSettings
from src.excel_generator.user_builder import (
    UserFullAnalyticReportSettings,
    UserShiftAnalyticReportSettings,
    UserTaskAnalyticReportSettings,
)


class AnalyticsService:
    """Сервис для получения отчётов."""

    def __init__(
        self,
        task_repository: TaskRepository = Depends(),
        shift_repository: ShiftRepository = Depends(),
        user_repository: UserRepository = Depends(),
        task_report_builder: AnalyticReportBuilder = Depends(),
    ) -> None:
        self.__workbook = task_report_builder
        self.__task_repository = task_repository
        self.__shift_repository = shift_repository
        self.__user_repository = user_repository

    @staticmethod
    async def __generate_task_report_description() -> str:
        """Генерация описания к отчёту с заданиями."""
        return f"Отчёт по задачам\nдата формирования отчёта: {date.today().strftime('%d.%m.%Y')}"

    async def __generate_task_report(self, workbook: Workbook) -> None:
        """Генерация отчёта с заданиями."""
        tasks_statistic = await self.__task_repository.get_tasks_statistics_report()
        description = await self.__generate_task_report_description()
        self.__workbook.add_sheet(
            description,
            tasks_statistic,
            workbook=workbook,
            analytic_report_settings=TaskAnalyticReportSettings,
        )

    async def __generate_shift_report_description(self, shift_id: UUID) -> str:
        """Генерация описания к отчёту по выбранной смене."""
        shift = await self.__shift_repository.get(shift_id)
        return (
            f"Отчёт по смене №{shift.sequence_number} ({shift.title})\n"
            f"дата старта: {shift.started_at.strftime('%d.%m.%Y')}\n"
            f"дата окончания: {shift.finished_at.strftime('%d.%m.%Y')}\n"
            f"дата формирования отчёта: {date.today().strftime('%d.%m.%Y')}"
        )

    async def __generate_report_for_shift(self, workbook: Workbook, shift_id: UUID) -> None:
        """Генерация отчёта по выбранной смене."""
        shift_statistic = await self.__shift_repository.get_shift_statistics_report_by_id(shift_id)
        description = await self.__generate_shift_report_description(shift_id)
        self.__workbook.add_sheet(
            description,
            shift_statistic,
            workbook=workbook,
            analytic_report_settings=ShiftAnalyticReportSettings,
        )

    async def generate_full_report(self) -> BytesIO:
        """Генерация полного отчёта."""
        workbook = self.__workbook.create_workbook()
        await self.__generate_task_report(workbook)
        await self.__generate_task_report(workbook)
        return self.__workbook.get_report_response(workbook)

    async def generate_task_report(self) -> BytesIO:
        """Генерация отчёта с заданиями."""
        workbook = self.__workbook.create_workbook()
        await self.__generate_task_report(workbook)
        return self.__workbook.get_report_response(workbook)

    async def generate_report_for_shift(self, shift_id: UUID) -> BytesIO:
        """Генерация отчёта по выбранной смене."""
        workbook = self.__workbook.create_workbook()
        await self.__generate_report_for_shift(workbook, shift_id)
        return self.__workbook.get_report_response(workbook)

    async def generate_shift_report_filename(self, shift_id: UUID) -> str:
        """Генерация названия файла отчета по смене."""
        shift = await self.__shift_repository.get(shift_id)
        shift_name = shift.title.replace(' ', '_').replace('.', '')
        filename = f"Отчёт_по_смене_№{shift.sequence_number}_{shift_name}_{date.today().strftime('%d-%m-%Y')}.xlsx"
        return quote_plus(filename)

    async def generate_user_report_filename(self, user_id: UUID) -> str:
        """Генерация названия файла отчета по участнику."""
        user = await self.__user_repository.get(user_id)
        user_full_name = f"{user.surname}_{user.name}"
        date_today = date.today().strftime('%d-%m-%Y')
        filename = f"Отчёт_по_участнику_{user_full_name}_{date_today}.xlsx"
        return quote_plus(filename)

    async def __generate_user_report_description(self, user_id: UUID) -> str:
        """Генерация описания к отчёту по участнику."""
        user = await self.__user_repository.get(user_id)
        return (
            f"Отчёт по участнику: {user.name} {user.surname}\n"
            f"Дата формирования отчёта: {date.today().strftime('%d.%m.%Y')}"
        )

    async def __add_sheets_to_user_report(self, workbook: Workbook, user_id: UUID) -> Workbook:
        """Генерация отчёта по участнику."""
        description = await self.__generate_user_report_description(user_id)

        user_task_statistic = await self.__user_repository.get_user_task_statistics_by_id_and_shift(user_id)
        self.__workbook.add_sheet(
            description,
            data=user_task_statistic,
            workbook=workbook,
            analytic_report_settings=UserTaskAnalyticReportSettings,
        )

        user_shift_statistic = await self.__user_repository.get_user_shift_statistics_by_id(user_id)
        self.__workbook.add_sheet(
            description,
            data=user_shift_statistic,
            workbook=workbook,
            analytic_report_settings=UserShiftAnalyticReportSettings,
        )

        all_tasks_data: dict[int, list] = dict()
        user_shift_and_task_report = UserFullAnalyticReportSettings()

        user_shifts = await self.__user_repository.get_user_shifts_titles(user_id)

        for shift in user_shifts:
            shift_tasks = await self.__user_repository.get_user_task_statistics_by_id_and_shift(user_id, shift.id)

            user_shift_and_task_report.add_shift(shift.title)

            for task in shift_tasks:
                all_tasks_data.setdefault(task.sequence_number, [task.sequence_number, task.title]).extend(
                    astuple(task)[2:]
                )

        self.__workbook.add_sheet(
            description,
            data=tuple(all_tasks_data.values()),
            workbook=workbook,
            analytic_report_settings=user_shift_and_task_report,
        )

        return workbook

    async def generate_report_for_user(self, user_id: UUID) -> BytesIO:
        """Генерация отчёта по участнику."""
        workbook = self.__workbook.create_workbook()
        await self.__add_sheets_to_user_report(workbook, user_id)
        return self.__workbook.get_report_response(workbook)
