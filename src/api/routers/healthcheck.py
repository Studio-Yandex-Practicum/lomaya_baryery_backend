from fastapi import APIRouter, Depends, Request
from fastapi_restful.cbv import cbv

from src.api.response_models.healthcheck import HealthcheckResponse
from src.core.services.healthcheck_service import HealthcheckService

router = APIRouter()


@cbv(router)
class HealthcheckCBV:
    healthcheck_service: HealthcheckService = Depends()

    @router.get(
        "/healthcheck",
        response_model=HealthcheckResponse,
        response_model_exclude_none=True,
        summary="Проверить работоспособность Бота, АПИ сервиса и БД.",
        response_description="Полная информация выводится в случае наличия ошибки.",
    )
    async def get_current_status(self, request: Request) -> HealthcheckResponse:
        """Запускает сервис проверки состояния Бота, АПИ, БД."""
        return await self.healthcheck_service.get_healthcheck_status(request.app.state.bot_instance.bot)
