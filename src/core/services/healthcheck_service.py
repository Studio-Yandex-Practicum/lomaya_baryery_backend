import logging
from datetime import datetime
from http import HTTPStatus

import aiohttp
from fastapi import Depends
from telegram.ext import Application

from src.api.response_models.healthcheck import (
    ComponentItemHealthcheck,
    HealthcheckResponse,
)
from src.core.db.repository import ReportRepository
from src.core.settings import settings


class HealthcheckService:
    def __init__(self, report_repository: ReportRepository = Depends()) -> None:
        self.__report_repository = report_repository

    async def __get_bot_status(self, bot: Application.bot) -> tuple:
        """Проверка, что бот запустился и работает корректно."""
        try:
            await bot.get_me()
            return ComponentItemHealthcheck(name='bot')
        except Exception as bot_error:
            logging.exception(bot_error)
            return ComponentItemHealthcheck(name='bot', status=False, errors=[f'{bot_error}'])

    async def __get_api_status(self) -> tuple:
        """Делает запрос к апи и проверяет, что апи отвечает."""
        async with aiohttp.ClientSession() as session:
            async with session.get(settings.HEALTHCHECK_API_URL) as response:
                if response.status == HTTPStatus.OK:
                    return ComponentItemHealthcheck(name='api')
                return ComponentItemHealthcheck(name='api', status=False, errors=[f'{response.status}'])

    async def __get_db_status(self) -> tuple:
        """Делает запрос к Базе Данных и проверяет, что приходит ответ."""
        try:
            await self.__report_repository.get_all_tasks_id_under_review()
            return ComponentItemHealthcheck(name='db')
        except Exception as db_error:
            logging.exception(db_error)
            return ComponentItemHealthcheck(name='db', status=False, errors=[f'{db_error}'])

    async def get_healthcheck_status(self, bot: Application.bot) -> HealthcheckResponse:
        components = [await self.__get_bot_status(bot), await self.__get_api_status(), await self.__get_db_status()]
        return HealthcheckResponse(timestamp=datetime.now(), components=components)
