from datetime import datetime

from fastapi import Depends

from src.api.request_models.administrator_mail_request import (
    AdministratorMailRequestRequest,
)
from src.core import settings
from src.core.db.models import AdministratorMailRequest
from src.core.db.repository import AdministratorMailRequestRepository


class AdministratorMailRequestService:
    def __init__(self, administrator_mail_request_repository: AdministratorMailRequestRepository = Depends()) -> None:
        self.__administrator_mail_request_repository = administrator_mail_request_repository

    async def create_mail_request(self, invitation_data: AdministratorMailRequestRequest) -> AdministratorMailRequest:
        """Создает в БД приглашение для регистрации нового администратора/психолога.

        Аргументы:
            invitation_data (AdministratorMailRequestRequest): предзаполненные администратором данные
        """
        expiration_date = datetime.utcnow() + settings.INVITE_LINK_EXPIRATION_TIME
        return await self.__administrator_mail_request_repository.create(
            AdministratorMailRequest(**invitation_data.dict(), expired_date=expiration_date)
        )
