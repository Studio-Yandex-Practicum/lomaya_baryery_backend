from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from fastapi_restful.cbv import cbv

from src.core.services.analytics_service import AnaliticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@cbv(router)
class AnalyticsCBV:
    analitics_service: AnaliticsService = Depends()

    @router.get(
        "/",
        response_class=StreamingResponse,
        status_code=HTTPStatus.OK,
        summary="Формирование полного отчёта",
    )
    async def generate_report_request(
        self,
    ) -> StreamingResponse:
        """Формирует excel файл со всеми отчётами."""
        return await self.analitics_service.generate_report()
