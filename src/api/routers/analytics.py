from datetime import datetime
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_restful.cbv import cbv

from src.api.response_models.error import generate_error_responses
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
        summary="Формирование полного отчёта",
    )
    async def generate_full_report(
        self,
    ) -> StreamingResponse:
        """Формирует excel файл со всеми отчётами."""
        filename = f"full_report_{datetime.now()}.xlsx"
        headers = {'Content-Disposition': f'attachment; filename={filename}'}
        workbook = await self._analytics_service.generate_full_report()
        return StreamingResponse(workbook, headers=headers)

    @router.get(
        "/tasks",
        response_model=None,
        response_class=StreamingResponse,
        status_code=HTTPStatus.OK,
        summary="Формирование отчёта c задачами",
    )
    async def generate_task_report(self) -> StreamingResponse:
        """
        Формирует отчёт с общей статистикой выполнения задач во всех сменах.

        Содержит:
        - cписок всех заданий;
        - общее количество принятых/отклонённых/не предоставленных отчётов по каждому заданию.
        """
        filename = f"tasks_report_{datetime.now()}.xlsx"
        headers = {'Content-Disposition': f'attachment; filename={filename}'}
        workbook = await self._analytics_service.generate_task_report()
        return StreamingResponse(workbook, headers=headers)

    @router.get(
        "/{shift_id}/shift_report",
        response_model=None,
        response_class=StreamingResponse,
        status_code=HTTPStatus.OK,
        summary="Формирование отчёта по выбранной смене",
        responses=generate_error_responses(HTTPStatus.NOT_FOUND),
    )
    async def generate_report_for_shift(self, shift_id: UUID) -> StreamingResponse:
        """
        Формирует отчёт по выбранной смене с общей статистикой для каждого задания.

        Содержит:
        - список всех задач;
        - количество отчетов принятых с 1-й/2-й/3-й попытки;
        - общее количество принятых/отклонённых/не предоставленных отчётов по каждому заданию.
        """
        filename = await self._analytics_service.generate_shift_report_filename(shift_id)
        headers = {'Content-Disposition': f'attachment; filename={filename}'}
        workbook = await self._analytics_service.generate_report_for_shift(shift_id)
        return StreamingResponse(workbook, headers=headers)

    @router.get(
        "/user/{user_id}",
        response_model=None,
        response_class=StreamingResponse,
        status_code=HTTPStatus.OK,
        summary="Формирование отчёта по пользователю",
        responses=generate_error_responses(HTTPStatus.NOT_FOUND),
    )
    async def generate_report_for_user(self, user_id: UUID) -> StreamingResponse:
        """Формирует отчёт по выбранному участнику.

        Отчёт содержит:
        - список всех задач;
            - количество отчетов, принятых с 1-й/2-й/3-й попытки по каждому заданию;
            - общее количество принятых/отклонённых/не предоставленных отчётов по каждому заданию;
        - список всех смен участника;
            - количество отчетов, принятых с 1-й/2-й/3-й попытки по каждой смене;
            - общее количество принятых/отклонённых/не предоставленных отчётов по каждой смене
        """
        filename = await self._analytics_service.generate_user_report_filename(user_id)
        headers = {'Content-Disposition': f'attachment; filename={filename}'}
        workbook = await self._analytics_service.generate_report_for_user(user_id)
        return StreamingResponse(workbook, headers=headers)
