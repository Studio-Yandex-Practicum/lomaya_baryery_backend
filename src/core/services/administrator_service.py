import datetime

from fastapi import Depends

from src.api.request_models.administrator import AdministratorRegistrationRequest
from src.api.response_models.administrator import AdministratorResponse
from src.core.db.models import Administrator
from src.core.db.repository import (
    AdministratorInvitationRepository,
    AdministratorRepository,
)
from src.core.services.authentication_service import PASSWORD_CONTEXT


class AdministratorService:
    def __init__(
        self,
        administrator_repository: AdministratorRepository = Depends(),
        administrator_invitation_repository: AdministratorInvitationRepository = Depends(),
    ):
        self.__administrator_repository = administrator_repository
        self.__administrator_invitation_repository = administrator_invitation_repository

    async def register_new_administrator(self, schema: AdministratorRegistrationRequest) -> AdministratorResponse:
        """Регистрация нового администратора. Устанавливает invitation.expired_date вчерашнюю дату."""
        dataset = schema.dict()
        token = dataset.pop("token", None)
        password = dataset.pop("password", None)
        invitation = await self.__administrator_invitation_repository.get_mail_request_by_token(token)
        administrator = Administrator(**dataset)
        administrator.status = Administrator.Status.ACTIVE
        administrator.email = invitation.email
        administrator.hashed_password = PASSWORD_CONTEXT.hash(password.get_secret_value())
        invitation.expired_date = datetime.date.today() - datetime.timedelta(days=1)
        await self.__administrator_repository.create(administrator)
        await self.__administrator_invitation_repository.update(invitation.id, invitation)
        return administrator

    async def get_administrators_filter_by_role_and_status(
        self,
        status: Administrator.Status,
        role: Administrator.Role,
    ) -> list[Administrator]:
        """Получает список администраторов, опционально отфильтрованых по роли и/или статусу."""
        return await self.__administrator_repository.get_administrators_filter_by_role_and_status(status, role)
