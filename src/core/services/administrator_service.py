import secrets
import string
from typing import Type
from uuid import UUID

from fastapi import Depends

from src.api.request_models.administrator import AdministratorRegistrationRequest
from src.core import exceptions
from src.core.db.models import Administrator
from src.core.db.repository import AdministratorRepository
from src.core.email import EmailProvider
from src.core.services.administrator_invitation import AdministratorInvitationService
from src.core.services.authentication_service import AuthenticationService


class AdministratorService:
    def __init__(
        self,
        administrator_repository: AdministratorRepository = Depends(),
        administrator_invitation_service: AdministratorInvitationService = Depends(),
        authentication_service: AuthenticationService = Depends(),
        email: EmailProvider = Depends(),
    ):
        self.__administrator_repository = administrator_repository
        self.__administrator_invitation_service = administrator_invitation_service
        self.__authentication_service = authentication_service
        self.__email = email

    def __create_new_password(self) -> str:
        """Создать новый пароль."""
        alphabet = string.ascii_lowercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(8))

    async def check_administrator_is_admin_by_email(self, email: str) -> bool:
        """Проверяет существование активного администратора с ролью admin по email.

        Проверяет есть ли в базе администратор, не заблокирован ли он и
        есть ли у него роль ADMINISTRATOR.
        Если одно из условий не выполняется, выбрасывается исключение.
        Если все условия выполняются — возвращает True.
        """
        administrator_exists = await self.__administrator_repository.administrator_is_active_and_is_admin(email)

        if not administrator_exists:
            raise exceptions.ForbiddenError

        return True

    async def register_new_administrator(self, token: UUID, schema: AdministratorRegistrationRequest) -> Administrator:
        """Регистрация нового администратора."""
        invitation = await self.__administrator_invitation_service.get_invitation_by_token(token)
        administrator = Administrator(
            name=schema.name,
            surname=schema.surname,
            email=invitation.email,
            hashed_password=AuthenticationService.get_hashed_password(schema.password.get_secret_value()),
            status=Administrator.Status.ACTIVE,
            role=Administrator.Role.EXPERT,
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

    async def restore_administrator_password(self, token: str, email: str) -> Administrator:
        """Сброс пароля администратора.

        Любой пользователь может сбросить пароль самому себе.
        Сбрасывать пароль другим администратором может только пользователь с ролью `Administrator.Role.ADMINISTRATOR`
        -Генерация нового пароля.
        -Хэширование нового пароля.
        -Сохранеине нового пароля в БД.
        -Отправка нового пароля на почту Администратору/Эксперту.
        """
        changer_email = self.__authentication_service.get_email_from_token(token)

        if changer_email != email:
            await self.check_administrator_is_admin_by_email(changer_email)

        password = self.__create_new_password()
        administrator = await self.__set_new_password(password, email)
        await self.__email.send_restored_password(password, email)
        return administrator  # noqa R: 504

    async def __set_new_password(self, password: str, email: str) -> Administrator:
        """Хэширует пароль, сохраняет его в БД, возвращает объект Administrator с обновленными данными."""
        hashed_password = AuthenticationService.get_hashed_password(password)
        administrator = await self.__administrator_repository.get_by_email(email)
        instance = Administrator(hashed_password=hashed_password)
        return await self.__administrator_repository.update(id=administrator.id, instance=instance)

    async def switch_a_field_with_checks(
        self, token: str, administrator_id: UUID, field: Type[Administrator.Status | Administrator.Role]
    ) -> Administrator:
        changer_email = self.__authentication_service.get_email_from_token(token)

        await self.check_administrator_is_admin_by_email(changer_email)

        administrator = await self.__administrator_repository.get(administrator_id)

        if administrator.email == changer_email:
            raise exceptions.AdministratorSelfChangeError

        administrator.switch_a_field(field)

        return await self.__administrator_repository.update(administrator.id, administrator)
