from fastapi import APIRouter, Depends

from src.core.services.check_health_service import CheckHealthService


router = APIRouter()


@router.get(
    "/healthcheck",
    summary="Проверить работоспособность Бота, АПИ сервиса и БД.",
    response_description="Полная информация выводится в случае наличия ошибки."
)
async def check_telegram_bot_and_api_and_db_startup(
        check_service: CheckHealthService = Depends(),
) -> dict[str, str]:
    """Запускает функции проверки состояния Бота, АПИ, БД."""
    check_api_endpoint = "hello"
    bot_status = await check_service.telegram_bot_status_callback()
    api_status = await check_service.api_status_callback(check_api_endpoint)
    db_status = await check_service.db_request_callback()
    return {
        "Bot_status": bot_status,
        "API_status": api_status,
        "DB_status": db_status
    }
