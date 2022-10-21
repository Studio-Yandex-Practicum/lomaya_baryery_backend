from fastapi import APIRouter, Depends

from src.api.response_models.health import HealthResponse
from src.core.services.health_service import HealthService


router = APIRouter()


@router.get(
    "/healthcheck",
    response_model=HealthResponse,
    summary="Проверить работоспособность Бота, АПИ сервиса и БД.",
    response_description="Полная информация выводится в случае наличия ошибки."
)
async def health_check(
        health_service: HealthService = Depends()
) -> HealthResponse:
    """Запускает сервис проверки состояния Бота, АПИ, БД."""
    return await health_service.health_check()
