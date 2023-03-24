import secrets
import string
from uuid import UUID

from fastapi import Depends

from src.api.request_models.administrator import AdministratorRegistrationRequest
from src.core import exceptions
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

    def __create_new_password(self) -> str:
        """Создать новый пароль."""
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(8))
        return password

    async def register_new_administrator(self, token: UUID, schema: AdministratorRegistrationRequest) -> Administrator:
        """Регистрация нового администратора."""
        invitation = await self.__administrator_invitation_service.get_invitation_by_token(token)
        administrator = Administrator(
            name=schema.name,
            surname=schema.surname,
            email=invitation.email,
            hashed_password=AuthenticationService.get_hashed_password(schema.password.get_secret_value()),
            status=Administrator.Status.ACTIVE,
            role=Administrator.Role.PSYCHOLOGIST,
        )
        administrator = await self.__administrator_repository.create(administrator)
        await self.__administrator_invitation_service.close_invitation(token)
        return administrator  # noqa: R504

    async def get_administrators_filter_by_role_and_status(
        self,
        status: Administrator.Status,
        role: Administrator.Role,
    ) -> list[Administrator]:
        """Получает список администраторов, опционально отфильтрованых по роли и/или статусу."""
        return await self.__administrator_repository.get_administrators_filter_by_role_and_status(status, role)

    async def switch_administrator_role(self, changed_by: Administrator, administrator_id: UUID) -> Administrator:
        """Переключает роль администратора."""
        if changed_by.role is not Administrator.Role.ADMINISTRATOR:
            raise exceptions.AdministratorChangeError

        # не надо менять роль самому себе
        if administrator_id == changed_by.id:
            raise exceptions.AdministratorSelfChangeRoleError

        administrator = await self.__administrator_repository.get(administrator_id)

        if administrator.role is Administrator.Role.ADMINISTRATOR:
            administrator.role = Administrator.Role.PSYCHOLOGIST
        else:
            administrator.role = Administrator.Role.ADMINISTRATOR

        return await self.__administrator_repository.update(administrator.id, administrator)

    async def administrator_reset_password(self, email: str) -> str:
        """
        Восстановление пароля администратора.

        -Генерация нового пароля.
        -Сохранеине нового пароля в БД.
        -Отпарвка нового пароля администратору/психологу.
        """
        password = self.__create_new_password()
        hashed_password = AuthenticationService.get_hashed_password(password)
        administrator = await self.__administrator_repository.get_by_email(email)
        instance = Administrator(hashed_password=hashed_password)
        await self.__administrator_repository.update(id=administrator.id, instance=instance)
        return password

    async def block_administrator(self, blocked_by: Administrator, blocked_id: UUID) -> Administrator:
        """Блокирует администратора."""
        if blocked_by.role is not Administrator.Role.ADMINISTRATOR:
            raise exceptions.AdministratorBlockError
        if blocked_by.id == blocked_id:
            raise exceptions.AdministratorSelfBlockError

        administrator = await self.__administrator_repository.get(blocked_id)
        if administrator.status is Administrator.Status.ACTIVE:
            administrator.status = Administrator.Status.BLOCKED
        else:
            administrator.status = Administrator.Status.ACTIVE
        return await self.__administrator_repository.update(administrator.id, administrator)
