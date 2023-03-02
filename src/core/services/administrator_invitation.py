from datetime import date, datetime, timedelta
from uuid import UUID

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
            AdministratorInvitation(**invitation_data.dict(), expired_datetime=expiration_date)
        )

    async def get_invitation_by_token(self, token: UUID) -> AdministratorInvitation:
        return await self.__administrator_mail_request_repository.get_mail_request_by_token(token)

    async def close_invitation(self, token: UUID) -> None:
        """Устанавливаем прошедшую дату в invitation.expired_datetime."""
        invitation = await self.__administrator_mail_request_repository.get_mail_request_by_token(token)
        invitation.expired_datetime = date.today() - timedelta(days=1)
        await self.__administrator_mail_request_repository.update(invitation.id, invitation)

    async def list_all_invitations(self) -> list[AdministratorInvitation]:
        return await self.__administrator_mail_request_repository.get_all()
