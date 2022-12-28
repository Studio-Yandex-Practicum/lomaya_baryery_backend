from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from fastapi_restful.cbv import cbv

from src.core.services.excel_report_service import ExcelReportService

router = APIRouter(prefix="/full-excel-report", tags=["Excel"])


@cbv(router)
class ExcelReportCBV:
    excel_report_service: ExcelReportService = Depends()

    @router.get(
        "/",
        response_class=StreamingResponse,
        status_code=HTTPStatus.OK,
        summary="Формирование полного отчёта",
    )
    async def get_task_excel_report_request(
        self,
    ) -> StreamingResponse:
        """Формирует excel файл со всеми отчётами."""
        return await self.excel_report_service.generate_full_report()
