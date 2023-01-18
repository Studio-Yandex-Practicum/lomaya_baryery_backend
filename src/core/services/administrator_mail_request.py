from fastapi import Depends

from src.api.request_models.administrator_mail_request import (
    AdministratorMailRequestRequest,
)
from src.core.db.models import AdministratorMailRequest
from src.core.db.repository import AdministratorMailRequestRepository
from src.core.exceptions import AdministratorMailRequestInvalid


class AdministratorMailRequestService:
    def __init__(
        self,
        administrator_mail_request_repository: AdministratorMailRequestRepository = Depends(),
    ) -> None:
        self.__administrator_mail_request_repository = administrator_mail_request_repository

    async def create_mail_request(self, invitation_data: AdministratorMailRequestRequest) -> AdministratorMailRequest:
        """Создает в БД приглашение для регистрации нового администратора/психолога.

        Аргументы:
            invitation_data (AdministratorMailRequestRequest): предзаполненные администратором данные
        """
        return await self.__administrator_mail_request_repository.create(
            AdministratorMailRequest(**invitation_data.dict())
        )

    async def get_active_mail_request(self, token: str) -> AdministratorMailRequest:
        """Возвращает действующее приглашение по токену.

        Аргументы:
            token (str): уникальный номер AdministratorMailRequest, используемый в ссылке для приглашения

        Вызывает исключение:
            AdministratorMailRequestInvalid: если записи с таким токеном нет или время приглашения истекло
        """
        mail_request = await self.__administrator_mail_request_repository.get_mail_request_by_token(token)
        if not mail_request:
            raise AdministratorMailRequestInvalid
        return mail_request
