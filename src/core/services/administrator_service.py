import datetime as dt

from uuid import UUID, uuid4

from fastapi import Depends

from src.api.request_models.administrator import AdministratorRegistrationRequest
from src.core.db.models import Administrator, AdministratorPasswordReset
from src.core.db.repository import AdministratorRepository, AdministratorPasswordResetRepository
from src.core.services.administrator_invitation import AdministratorInvitationService
from src.core.services.authentication_service import AuthenticationService


class AdministratorService:
    def __init__(
        self,
        administrator_repository: AdministratorRepository = Depends(),
        administrator_password_reset: AdministratorPasswordResetRepository = Depends(),
        administrator_invitation_service: AdministratorInvitationService = Depends(),
    ):
        self.__administrator_repository = administrator_repository
        self.__administrator_invitation_service = administrator_invitation_service
        self.__administrator_password_reset = administrator_password_reset

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

    async def get_by_email(self, email: Administrator.email) -> Administrator:
        """Получение администратора по email."""
        return await self.__administrator_repository.get_by_email(email)

    async def create_password_reset_object(self, email: str) -> AdministratorPasswordReset:
        """
        Создание объекта AdministratorPasswordReset:
        -Объект служит для создания связки email и токена участвующего в генерации ссылки
        для восстановления пароля.
        -Объект создается с целью исключения существования одновременно нескольких рабочих ссылок.
        -При каждом запросе на эндпоинт /password_reset запись в БД обновляется.
        """
        administrator_password_reset = await self.__administrator_password_reset.get_administrator_password_reset(email)
        instance = AdministratorPasswordReset(
            email = email,
            token = str(uuid4()),
            expired_datetime = dt.datetime.utcnow()
        )
        if administrator_password_reset:
            await self.__administrator_password_reset.update(administrator_password_reset.id, instance)
        else:
            await self.__administrator_password_reset.create(instance)
        return administrator_password_reset
