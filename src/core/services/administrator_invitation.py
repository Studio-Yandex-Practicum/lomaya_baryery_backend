from datetime import date, datetime, timedelta
from uuid import UUID

from fastapi import Depends

from src.api.request_models.administrator_invitation import (
    AdministratorInvitationRequest,
)
from src.core import settings
from src.core.db.models import AdministratorInvitation
from src.core.db.repository import (
    AdministratorInvitationRepository,
    AdministratorRepository,
)
from src.core.exceptions import (
    AdministratorAlreadyExistsError,
    InvitationAlreadyActivatedError,
    InvitationAlreadyDeactivatedError,
)


class AdministratorInvitationService:
    def __init__(
        self,
        administrator_mail_request_repository: AdministratorInvitationRepository = Depends(),
        administrator_repository: AdministratorRepository = Depends(),
    ) -> None:
        self.__administrator_mail_request_repository = administrator_mail_request_repository
        self.__administrator_repository = administrator_repository

    async def create_mail_request(self, invitation_data: AdministratorInvitationRequest) -> AdministratorInvitation:
        """Создает в БД приглашение для регистрации нового администратора/'эксперта'.

        Аргументы:
            invitation_data (AdministratorMailRequestRequest): предзаполненные администратором данные
        """
        if await self.__administrator_repository.check_administrator_existence(invitation_data.email):
            raise AdministratorAlreadyExistsError
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

    async def get_invitation_by_id(self, invitation_id: UUID) -> AdministratorInvitation:
        return await self.__administrator_mail_request_repository.get(invitation_id)

    async def deactivate_invitation(self, invitation_id: UUID) -> AdministratorInvitation:
        invitation = await self.get_invitation_by_id(invitation_id)
        if invitation.expired_datetime < datetime.now():
            raise InvitationAlreadyDeactivatedError
        invitation.expired_datetime = datetime.now() - timedelta(days=1)
        await self.__administrator_mail_request_repository.update(invitation_id, invitation)
        return invitation

    async def reactivate_invitation(self, invitation_id: UUID) -> AdministratorInvitation:
        invitation = await self.get_invitation_by_id(invitation_id)
        if invitation.expired_datetime > datetime.now():
            raise InvitationAlreadyActivatedError
        invitation.expired_datetime = datetime.utcnow() + settings.INVITE_LINK_EXPIRATION_TIME
        await self.__administrator_mail_request_repository.update(invitation_id, invitation)
        return invitation
