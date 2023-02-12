from uuid import UUID

from fastapi import Depends

from src.api.request_models.administrator import AdministratorRegistrationRequest
from src.api.response_models.administrator import AdministratorResponse
from src.core.db.models import Administrator
from src.core.db.repository import AdministratorRepository
from src.core.services.administrator_invitation import AdministratorInvitationService
from src.core.services.authentication_service import AuthenticationService


class AdministratorService:
    def __init__(
        self,
        administrator_repository: AdministratorRepository = Depends(),
        administrator_invitation_service: AdministratorInvitationService = Depends(),
    ):
        self.__administrator_repository = administrator_repository
        self.__administrator_invitation_service = administrator_invitation_service

    async def register_new_administrator(
        self, token: UUID, schema: AdministratorRegistrationRequest
    ) -> AdministratorResponse:
        """Регистрация нового администратора."""
        invitation = await self.__administrator_invitation_service.get_invitation_by_token(token)
        administrator = await schema.parse_to_db_obj()
        administrator.email = invitation.email
        administrator.hashed_password = AuthenticationService.get_hashed_password(schema.password.get_secret_value())
        administrator = await self.__administrator_repository.create(administrator)
        await self.__administrator_invitation_service.close_invitation(token)
        return AdministratorResponse(
            id=administrator.id,
            name=administrator.name,
            surname=administrator.surname,
            email=administrator.email,
            role=administrator.role,
            status=administrator.status,
            last_login_at=administrator.last_login_at,
        )

    async def get_administrators_filter_by_role_and_status(
        self,
        status: Administrator.Status,
        role: Administrator.Role,
    ) -> list[Administrator]:
        """Получает список администраторов, опционально отфильтрованых по роли и/или статусу."""
        return await self.__administrator_repository.get_administrators_filter_by_role_and_status(status, role)
