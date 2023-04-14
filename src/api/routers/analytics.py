from http import HTTPStatus

from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import StreamingResponse
from fastapi_restful.cbv import cbv

from src.core.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@cbv(router)
class AnalyticsCBV:
    _analytics_service: AnalyticsService = Depends()
    _token: HTTPAuthorizationCredentials = Depends(HTTPBearer())

    @router.get(
        "/total",
        response_model=None,
        response_class=StreamingResponse,
        status_code=HTTPStatus.OK,
        summary="Формирование полного отчёта"
    )
    async def generate_full_report(
        self,
    ) -> StreamingResponse:
        """Формирует excel файл со всеми отчётами."""
        filename = f"report_{datetime.now()}.xlsx"
        headers = {'Content-Disposition': f'attachment; filename={filename}'}
        workbook = await self._analytics_service.generate_full_report()
        return StreamingResponse(workbook, headers=headers)

    @router.get(
        "/tasks",
        response_model=None,
        response_class=StreamingResponse,
        status_code=HTTPStatus.OK,
        summary="Формирование отчёта c задачами"
    )
    async def generate_task_report(self) -> StreamingResponse:
        """
        Формирует отчёт с общей статистикой выполнения задач во всех сменах.

        Содержит:
        - cписок всех заданий;
        - общее количество принятых/отклонённых/не предоставленных отчётов по каждому заданию.
        """
        filename = f"report_{datetime.now()}.xlsx"
        headers = {'Content-Disposition': f'attachment; filename={filename}'}
        workbook = await self._analytics_service.generate_task_report()
        return StreamingResponse(workbook, headers=headers)
