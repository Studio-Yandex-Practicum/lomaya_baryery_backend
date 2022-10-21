import logging
from http import HTTPStatus

import aiohttp
from fastapi import Depends

from src.api.response_models.healthcheck import HealthcheckResponse
from src.bot.services import bot
from src.core.db.repository.healthcheck_repository import HealthcheckRepository


class HealthcheckService:
    def __init__(self, healthcheck_repository: HealthcheckRepository = Depends()) -> None:
        self.healthcheck_repository = healthcheck_repository

    async def bot_status_callback(self) -> str:
        """Проверка, что бот запустился и работает корректно."""
        try:
            bot_response = await bot.get_me()
            bot_status = f"Бот {bot_response.first_name} успешно запущен"
        except Exception as bot_error:
            logging.exception(bot_error)
            bot_status = f"Бот не запустился по причине: {bot_error}"
        finally:
            return bot_status

    async def api_status_callback(self, api_host: str, api_port: int, api_endpoint: str) -> str:
        """Делает запрос к апи и проверяет, что апи отвечает."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{api_host}:{api_port}/{api_endpoint}") as api_response:
                if api_response.status == HTTPStatus.OK:
                    return "API работает корректно"
                return f"API не работает, код ответа:{api_response.status}"

    async def db_status_callback(self) -> str:
        """Делает запрос к Базе Данных и проверяет, что приходит ответ."""
        try:
            await self.healthcheck_repository.get_db_ver()
            db_status = "База данных работает корректно"
        except Exception as db_error:
            logging.exception(db_error)
            db_status = f"База данных не работает по причине {db_error}"
        finally:
            return db_status

    async def health_check(self) -> HealthcheckResponse:
        return HealthcheckResponse(
            bot_status=await self.bot_status_callback(),
            api_status=await self.api_status_callback("http://localhost", 8080, "hello"),
            db_status=await self.db_status_callback(),
        )
