import json
from datetime import datetime

from fastapi import Depends
from fastapi.responses import StreamingResponse
from pydantic.schema import UUID

from src.core.db.models import Shift, Task
from src.core.db.repository.task_repository import TaskRepository
from src.core.exceptions import TodayTaskNotFoundError
from src.core.services.excel_report_service import ExcelReportService


class TaskService:
    def __init__(
        self, task_repository: TaskRepository = Depends(), excel_report_service: ExcelReportService = Depends()
    ) -> None:
        self.__task_repository = task_repository
        self.__excel_report_service = excel_report_service

    async def get_task_ids_list(
        self,
    ) -> list[UUID]:
        return await self.__task_repository.get_task_ids_list()

    async def get_task_by_day_of_month(self, tasks: Shift.tasks, day_of_month: int) -> Task:
        tasks_dict = json.loads(tasks)
        task_id = tasks_dict.get(str(day_of_month))
        task = await self.__task_repository.get_or_none(task_id)
        if not task:
            raise TodayTaskNotFoundError()
        return task

    async def get_tasks_statistics_report(self) -> StreamingResponse:

        workbook = await self.__excel_report_service.get_report_template(ExcelReportService.Sheets.TASKS)
        await self.__excel_report_service.create_tasks_statistics_report(workbook)
        stream = await self.__excel_report_service.save_report_to_stream(workbook)

        filename = f"tasks_report_{datetime.now()}.xlsx"
        headers = {'Content-Disposition': f'attachment; filename={filename}'}
        return StreamingResponse(stream, headers=headers)
