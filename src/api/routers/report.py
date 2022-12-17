from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi_restful.cbv import cbv
from pydantic.schema import UUID

from src.api.response_models.report import ReportResponse, ReportSummaryResponse
from src.core.db.models import Report
from src.core.services.report_service import ReportService
from src.core.services.shift_service import ShiftService

router = APIRouter(prefix="/reports", tags=["Report"])


@cbv(router)
class ReportsCBV:
    shift_service: ShiftService = Depends()
    report_service: ReportService = Depends()

    @router.get(
        "/{report_id}",
        response_model=ReportResponse,
        response_model_exclude_none=True,
        status_code=HTTPStatus.OK,
        summary="Получить информацию об отчёте участника.",
        response_description="Полная информация об отчёте участника.",
    )
    async def get_user_report(
        self,
        report_id: UUID,
    ) -> dict:
        """Вернуть отчет участника.

        - **user_id**:номер участника
        - **report_id**: номер задачи, назначенной участнику на день смены (генерируется рандомно при старте смены)
        - **task_id**: номер задачи
        - **task_date**: дата получения задания
        - **status**: статус задачи
        - **photo_url**: url фото выполненной задачи
        """
        return await self.report_service.get_report_with_report_url(report_id)

    @router.patch(
        "/{report_id}/approve",
        status_code=HTTPStatus.OK,
        summary="Принять задание. Будет начислен 1 \"ломбарьерчик\".",
    )
    async def approve_task_status(
        self,
        report_id: UUID,
        request: Request,
    ) -> HTTPStatus.OK:
        """Отчет участника проверен и принят."""
        return await self.report_service.approve_report(report_id, request.app.state.bot_instance)

    @router.patch("/{report_id}/decline", status_code=HTTPStatus.OK, summary="Отклонить задание.")
    async def decline_task_status(
        self,
        report_id: UUID,
        request: Request,
    ) -> HTTPStatus.OK:
        """Отчет участника проверен и отклонен."""
        return await self.report_service.decline_report(report_id, request.app.state.bot_instance)

    @router.get(
        "/",
        response_model=list[ReportSummaryResponse],
        summary="Получения списка заданий пользователя по полям status и shift_id.",
    )
    async def get_report_summary(
        self,
        shift_id: UUID = None,
        status: Report.Status = None,
    ) -> list[ReportSummaryResponse]:
        """
        Получения списка задач на проверку с возможностью фильтрации по полям status и shift_id.

        Список формируется по убыванию поля started_at.

        В запросе передаётся:

        - **shift_id**: уникальный id смены, ожидается в формате UUID.uuid4
        - **report.status**: статус задачи
        """
        return await self.report_service.get_summaries_of_reports(shift_id, status)
