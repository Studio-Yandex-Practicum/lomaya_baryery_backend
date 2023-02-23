from datetime import datetime

from fastapi import Depends

from src.api.request_models.administrator_invitation import (
    AdministratorInvitationRequest,
)
from src.core import settings
from src.core.db.models import AdministratorInvitation
from src.core.db.repository import AdministratorInvitationRepository


class AdministratorInvitationService:
    def __init__(self, administrator_mail_request_repository: AdministratorInvitationRepository = Depends()) -> None:
        self.__administrator_mail_request_repository = administrator_mail_request_repository

    async def create_mail_request(self, invitation_data: AdministratorInvitationRequest) -> AdministratorInvitation:
        """Создает в БД приглашение для регистрации нового администратора/психолога.

        Аргументы:
            invitation_data (AdministratorMailRequestRequest): предзаполненные администратором данные
        """
        expiration_date = datetime.utcnow() + settings.INVITE_LINK_EXPIRATION_TIME
        return await self.__administrator_mail_request_repository.create(
            AdministratorInvitation(**invitation_data.dict(), expired_date=expiration_date)
        )

    async def list_all_invitations(self) -> list[AdministratorInvitation]:
        """Возвращает список всех приглашений администраторов."""
        return await self.__administrator_mail_request_repository.get_all()
