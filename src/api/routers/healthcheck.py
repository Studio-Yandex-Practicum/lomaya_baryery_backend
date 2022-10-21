from fastapi import APIRouter, Depends

from src.api.response_models.healthcheck import HealthcheckResponse
from src.core.services.healthcheck_service import HealthcheckService

router = APIRouter()


@router.get(
    "/healthcheck",
    response_model=HealthcheckResponse,
    summary="Проверить работоспособность Бота, АПИ сервиса и БД.",
    response_description="Полная информация выводится в случае наличия ошибки.",
)
async def healthcheck(healthcheck_service: HealthcheckService = Depends()) -> HealthcheckResponse:
    """Запускает сервис проверки состояния Бота, АПИ, БД."""
    return await healthcheck_service.health_check()
