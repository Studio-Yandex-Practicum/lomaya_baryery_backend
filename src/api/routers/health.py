import logging
from http import HTTPStatus

import aiohttp
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.services import bot
from src.core.db.db import get_session
from src.core.db.models import User
from src.core.settings import settings

router = APIRouter()


@router.get(
    "/healthcheck",
    summary="Проверить работоспособность Бота, АПИ сервиса и БД.",
    response_description="Полная информация выводится в случае наличия ошибки."
)
async def check_telegram_bot_and_api_and_db_startup(
        session: AsyncSession = Depends(get_session)
) -> dict[str, str]:
    """Запускает функции проверки состояния Бота, АПИ, БД."""
    check_api_endpoint = "hello"
    bot_status = await check_telegram_bot_status_callback()
    api_status = await check_api_status_callback(check_api_endpoint)
    db_status = await check_db_request_callback(session)
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
                bot_status_response.is_bot,
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
        check_api_endpoint: str
) -> str:
    """Делает запрос к апи и проверяет, что апи отвечает.

    Заготовка с root_dir и api_url для тестов на ngrok:
    - root_dir = Path(__file__).parent.parent.parts[2]
    - api_url = f"{settings.APPLICATION_URL}/{root_dir}/{check_api_endpoint}"
    """
    api_url = f"http://127.0.0.1:8080/{check_api_endpoint}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as api_response:
            if api_response.status == HTTPStatus.OK:
                api_status = "API работает корректно"
            else:
                api_status = (
                    f"API не работает, код ответа:{api_response.status}"
                )
        return api_status


async def check_db_request_callback(
        session: AsyncSession
) -> str:
    """Делает запрос к Базе Данных и проверяет, что приходит ответ."""
    try:
        db_response_data = await session.execute(select(User.id))
        db_response_data = db_response_data.scalars().all()
        if db_response_data is not None:
            db_status = "База данных работает корректно"
    except Exception as db_error:
        logging.exception(db_error)
        db_status = f"База данных не работает по причине {db_error}"
    finally:
        return db_status
