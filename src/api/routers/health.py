import logging
from uuid import UUID

import aiohttp
from http import HTTPStatus
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.response_models.shift import ShiftUsersResponse
from src.bot.services import bot
from src.core.settings import settings

from src.core.db.repository import AbstractRepository, ShiftRepository
from src.core.services.shift_service import ShiftService


router = APIRouter()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


# logger = logging.getLogger(__name__)


@router.get("/healthcheck")
async def check_telegram_bot_and_api_and_db_startup() -> dict[str, str]:
    api_check_endpoint = "hello"
    check_shift_id = '2e934c94-fc1e-48ec-8439-9439d594c46f'
    bot_status = await check_telegram_bot_status_callback()
    api_status = await check_api_status_callback(api_check_endpoint)
    db_status = await check_db_request_callback(check_shift_id)
    return {
        "Bot_status": bot_status,
        "API_status": api_status,
        "DB_status": db_status
    }


async def check_telegram_bot_status_callback() -> str:
    """Проверка, что бот запустился и работает корректно."""
    try:
        bot_status_response = await bot.get_me()
        if bot_status_response is not None and (
                bot_status_response.is_bot is True,
                bot_status_response.id == settings.BOT_TOKEN.split(':')[0]
        ):
            bot_status = (
                f"Бот {bot_status_response.first_name} успешно запущен"
            )
    except Exception as bot_error:
        logging.exception(bot_error)
        bot_status = f"Бот не запустился по причине: {bot_error}"
    finally:
        return bot_status


async def check_api_status_callback(
        api_check_endpoint: str,
) -> str:
    """Делает запрос к апи и проверяет, что апи отвечает"""
    # заготовка с root_dir и api_url для тестов на ngrok
    # root_dir = Path(__file__).parent.parent.parts[2]
    # api_url = f"{settings.APPLICATION_URL}/{root_dir}/{api_check_endpoint}"
    api_url = f"http://127.0.0.1:8080/{api_check_endpoint}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as api_response:
            if api_response.status == HTTPStatus.OK:
                api_status = f"API работает корректно"
            api_status = f"API не работает, код ответа: {api_response.status}"
        return api_status


async def check_db_request_callback(
        shift_id: UUID
) -> ShiftUsersResponse:
    """Делает запрос к Базе Данных и проверяет, что приходит ответ"""
    shift_service = ShiftService()
    try:
        db_users = await shift_service.get_users_list(shift_id)
        print(db_users)
        if db_users and db_users is not None:
            db_status = "База данных работает корректно"
    except Exception as db_error:
        logging.exception(db_error)
        db_status = f"База данных не работает по причине {db_error}"
    finally:
        return db_status
