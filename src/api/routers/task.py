from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from fastapi_restful.cbv import cbv

from src.core.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Task"])


@cbv(router)
class TaskCBV:
    task_service: TaskService = Depends()

    @router.get(
        "/report",
        response_class=StreamingResponse,
        status_code=HTTPStatus.OK,
        summary="Формирования отчёта по задачам.",
    )
    async def get_task_excel_report_request(
        self,
    ) -> StreamingResponse:
        """Формирует excel файл со сведениями о задачах по всем сменам.

        Содержит:
        - cписок всех заданий;
        - общее количество принятых/отклонённых/непредоставленных отчётов по каждому заданию.
        """
        return await self.task_service.get_task_excel_report()
