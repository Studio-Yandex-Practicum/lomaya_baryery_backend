import enum
from datetime import datetime
from io import BytesIO

from fastapi import Depends
from fastapi.responses import StreamingResponse
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from src.core.db.repository.task_repository import TaskRepository
from src.core.settings import settings


class ExcelReportService:
    """Сервис для создания excel отчётов.

    Для генерации определённого отчёта при вызове метода get_report_template()
    передавайте в него sheet_name и используйте совместно с нужным методом. Например, метод
    create_tasks_statistics_report используется для получения статистики по задачам.

    Для генерации полного отчёта используйте метод generate_full_report().

    Возможные варианты sheet_name указаны в классе Sheets.
    При добавлении новых sheet_name они должны соответстовать названиям листов в шаблоне.
    """

    def __init__(self, task_repository: TaskRepository = Depends()) -> None:
        self.__task_repository = task_repository

    async def get_report_template(self, sheet_name: str | None = None) -> Workbook:
        """Возвращает excel шаблон.

        Если указан sheet_name, то удаляем все листы из шаблона кроме указанного.
        """
        workbook = load_workbook(settings.report_template_path)
        workbook.template = False
        if sheet_name:
            sheetnames = workbook.sheetnames
            for name in sheetnames:
                if name != sheet_name:
                    workbook.remove(workbook[name])
        return workbook

    async def save_report_to_stream(self, workbook: Workbook) -> BytesIO:
        stream = BytesIO()
        workbook.save(stream)
        stream.seek(0)
        return stream

    async def generate_full_report(self) -> StreamingResponse:
        """Создаёт полный excel отчёт."""
        workbook = await self.get_report_template()
        # создание отчётов
        await self.create_tasks_statistics_report(workbook)
        await self.create_test_report(workbook)
        stream = await self.save_report_to_stream(workbook)
        filename = f"report_{datetime.now()}.xlsx"
        headers = {'Content-Disposition': f'attachment; filename={filename}'}
        return StreamingResponse(stream, headers=headers)

    async def create_tasks_statistics_report(self, workbook: Workbook) -> Worksheet:
        tasks_report = await self.__task_repository.get_tasks_statistics_report()
        sheet = workbook[self.Sheets.TASKS]
        for idx, task in enumerate(tasks_report):
            row_num = idx + 2
            sheet.cell(row=row_num, column=1, value=task.description)
            sheet.cell(row=row_num, column=2, value=task.approved)
            sheet.cell(row=row_num, column=3, value=task.declined)
            sheet.cell(row=row_num, column=4, value=task.waiting)
        return sheet

    async def create_test_report(self, workbook: Workbook) -> Worksheet:
        sheet = workbook[self.Sheets.TEST]
        sheet.cell(row=1, column=1, value="тест")
        return sheet

    class Sheets(str, enum.Enum):
        TASKS = "Задачи"
        TEST = "Тест"
