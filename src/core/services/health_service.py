import logging
from http import HTTPStatus

import aiohttp
from fastapi import Depends

from src.bot.services import bot
from src.core.db.repository.health_repository import HealthRepository


class HealthService:
    def __init__(
            self, health_repository: HealthRepository = Depends()
    ) -> None:
        self.health_repository = health_repository

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

    async def api_status_callback(self, check_api_endpoint: str) -> str:
        """Делает запрос к апи и проверяет, что апи отвечает."""
        api_url = f"http://127.0.0.1:8080/{check_api_endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as api_response:
                if api_response.status == HTTPStatus.OK:
                    return "API работает корректно"
                return f"API не работает, код ответа:{api_response.status}"

    async def db_status_callback(self, db_table: str) -> str:
        """Делает запрос к Базе Данных и проверяет, что приходит ответ."""
        try:
            await self.health_repository.get_db_ver(db_table)
            db_status = "База данных работает корректно"
        except Exception as db_error:
            logging.exception(db_error)
            db_status = f"База данных не работает по причине {db_error}"
        finally:
            return db_status

    async def health_check(self) -> dict[str, str]:
        bot_status = await self.bot_status_callback()
        api_status = await self.api_status_callback("hello")
        db_status = await self.db_status_callback("alembic_version")
        return {
            "bot_status": bot_status,
            "api_status": api_status,
            "db_status": db_status,
        }
