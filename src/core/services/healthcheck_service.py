import logging

import aiohttp
from fastapi import Depends

from src.api.response_models.healthcheck import HealthcheckResponse
from src.bot.services import bot
from src.core.db.repository import UserTaskRepository
from src.core.settings import settings


class HealthcheckService:
    def __init__(self, user_task_repository: UserTaskRepository = Depends()) -> None:
        self.__user_task_repository = user_task_repository
        self.__errors = []

    async def __get_bot_status(self) -> bool:
        """Проверка, что бот запустился и работает корректно."""
        try:
            await bot.get_me()
            bot_status = True
        except Exception as bot_error:
            logging.exception(bot_error)
            self.__errors.append(f"{bot_error}")
            bot_status = False
        return bot_status

    async def __get_api_status(self) -> bool:
        """Делает запрос к апи и проверяет, что апи отвечает."""
        try:
            async with aiohttp.ClientSession() as session:
                await session.get(settings.HEALTHCHECK_API_URL)
                api_status = True
        except Exception as api_error:
            logging.exception(api_error)
            self.__errors.append(f"{api_error}")
            api_status = False
        return api_status

    async def __get_db_status(self) -> bool:
        """Делает запрос к Базе Данных и проверяет, что приходит ответ."""
        try:
            await self.__user_task_repository.get_all_tasks_id_under_review()
            db_status = True
        except Exception as db_error:
            logging.exception(db_error)
            self.__errors.append(f"{db_error}")
            db_status = False
        return db_status

    async def get_healthcheck_status(self) -> HealthcheckResponse:
        return HealthcheckResponse(
            bot_status=await self.__get_bot_status(),
            api_status=await self.__get_api_status(),
            db_status=await self.__get_db_status(),
            errors=self.__errors,
        )
