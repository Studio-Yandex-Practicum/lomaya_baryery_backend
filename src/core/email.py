from typing import Any

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr

from src.core import exceptions
from src.core.settings import settings


class EmailSchema(BaseModel):
    recipients: list[EmailStr]
    template_body: dict[str, Any] | None


class EmailProvider:
    """Класс для отправки электронных писем."""

    @staticmethod
    async def __send_mail(
        email_obj: EmailSchema,
        subject: str,
        template_name: str,
    ) -> None:
        """Базовый метод отправки сообщения на электронную почту.

        Аргументы:
            recipients (list[EmailStr]): список email получателей
            template_body (dict[str, Any]): значения переменных для шаблона сообщения
            subject (str): тема сообщения
            template_name (str): название шаблона для сообщения
        """
        conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_LOGIN,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.ORGANIZATIONS_EMAIL,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            # MAIL_FROM_NAME="Администрация \"Ломая Барьеры\"",
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=settings.USE_CREDENTIALS,
            VALIDATE_CERTS=settings.VALIDATE_CERTS,
            TEMPLATE_FOLDER=settings.email_template_directory,
        )
        message = MessageSchema(
            subject=subject,
            recipients=email_obj.recipients,
            template_body=email_obj.template_body,
            subtype=MessageType.html,
        )

        fastmail = FastMail(conf)
        try:
            await fastmail.send_message(message, template_name)
        except Exception as exc:
            raise exceptions.EmailSendError(email_obj.recipients, exc)

    async def send_invitation_link(self, url: str, name: str, email: str) -> None:
        """Отправляет указанным адресатам ссылку для регистрации в проекте.

        Аргументы:
            email (str): email получателя
            url (str): ссылка для регистрации
            name (str): имя получателя
        """
        template_body = {"url": url, "name": name}
        recipients = [email]
        email_obj = EmailSchema(recipients=recipients, template_body=template_body)
        await self.__send_mail(
            email_obj,
            "Приглашение в проект \"Ломая Барьеры\"",
            "send_invitation_link.html",
        )

    async def send_restored_password(self, password: str, email: str) -> None:
        """Отправляет email на почтовый ящик администратора/эксперта с новым паролем."""
        template_body = {"password": password}
        recipients = [email]
        email_obj = EmailSchema(recipients=recipients, template_body=template_body)
        await self.__send_mail(
            email_obj,
            "Восстановленный пароль от учетной записи в проекте \"Ломая Барьеры\"",
            "send_password_restore_email.html",
        )
