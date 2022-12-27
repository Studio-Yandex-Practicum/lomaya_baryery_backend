import csv
import io
import json
from datetime import datetime

from fastapi import Depends
from fastapi.responses import StreamingResponse
from pydantic.schema import UUID

from src.core.db.models import Shift, Task
from src.core.db.repository.task_repository import TaskRepository
from src.core.exceptions import ReportsNotFoundException, TodayTaskNotFoundError


class TaskService:
    def __init__(self, task_repository: TaskRepository = Depends()) -> None:
        self.__task_repository = task_repository

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

    async def get_task_excel_report(self):
        tasks_report = await self.__task_repository.get_tasks_report()
        if not tasks_report:
            raise ReportsNotFoundException()
        output = io.StringIO()
        writer = csv.writer(output, dialect='excel')
        header = (
            "Задача",
            "Кол-во принятых отчётов",
            "Кол-во отклонённых отчётов",
            "Кол-во не предоставленных отчётов",
        )
        writer.writerow(header)
        for task in tasks_report:
            writer.writerow((task.description, task.approved, task.declined, task.waiting))
        output.seek(0)
        filename = f"tasks_report_{datetime.now()}.csv"
        headers = {'Content-Disposition': f'attachment; filename={filename}'}
        return StreamingResponse(output, headers=headers, media_type="text/csv")
