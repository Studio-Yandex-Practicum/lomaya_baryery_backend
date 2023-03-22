import datetime as dt
from uuid import UUID, uuid4

from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates

from src.api.request_models.administrator import AdministratorRegistrationRequest
from src.core.db.models import Administrator, AdministratorPasswordReset
from src.core.db.repository import (
    AdministratorPasswordResetRepository,
    AdministratorRepository,
)
from src.core.services.administrator_invitation import AdministratorInvitationService
from src.core.services.authentication_service import AuthenticationService

templates = Jinja2Templates(directory="src/templates/email")


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
        Создание объекта AdministratorPasswordReset.

        -Объект служит для создания связки email и токена участвующего в генерации ссылки
        для восстановления пароля.
        -Объект создается с целью исключения существования одновременно нескольких рабочих ссылок.
        -При каждом запросе на эндпоинт /password_reset запись в БД обновляется.
        """
        administrator_password_reset = (
            await self.__administrator_password_reset.get_administrator_password_reset_by_email(email)
        )
        instance = AdministratorPasswordReset(token=str(uuid4()), email=email, expired_datetime=dt.datetime.utcnow())
        if administrator_password_reset:
            await self.__administrator_password_reset.update(administrator_password_reset.id, instance)
        else:
            await self.__administrator_password_reset.create(instance)
        return await self.__administrator_password_reset.get_administrator_password_reset_by_email(email)

    async def send_restore_form(self, request: Request, token: str):
        """
        Отправка пользователю формы.

        -В случае прохождения валидации пользователь перенаправляется на страницу с
        формой восстановления пароля.
        -В случае провала проверки времени жизни объекта AdministratorPasswordReset
        пользователь перенаправляется на страницу с просьбой повторно запросить ссылку
        на восстановление пароля.
        """
        if await self.__administrator_password_reset.administrator_password_reset_object_validation(token):
            return templates.TemplateResponse("reset_password_form.html", {"request": Request, "token": token})
        return templates.TemplateResponse(
            "reset_password_reject.html",
            {
                "request": request,
                "token": token,
                "text": "Ссылка устарела, пожалуйста, перейдите на страницу восстановления пароля повторно.",
            },
        )

    async def save_new_password(self, token: str, password: str) -> None:
        """Хэширование и сохранение пового пароля в БД."""
        administrator = await self.__administrator_password_reset.get_administrator_by_token(token)
        instance = Administrator(hashed_password=AuthenticationService.get_hashed_password(password))
        return await self.__administrator_repository.update(id=administrator.id, instance=instance)
