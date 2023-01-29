from typing import Any

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr

from src.core.exceptions import EmailSendException
from src.core.settings import ORGANIZATIONS_EMAIL, settings


class EmailSchema(BaseModel):
    recipients: list[EmailStr]
    template_body: dict[str, Any] | None


class EmailProvider:
    """Класс для отправки электронных писем."""

    async def __send_mail(
        self,
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
            MAIL_FROM=ORGANIZATIONS_EMAIL,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME="Администрация \"Ломая Барьеры\"",
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
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
            raise EmailSendException(email_obj.recipients, exc)

    async def send_invitation_link(self, url: str, name: str, email: EmailStr) -> None:
        """Отправляет указанным адресатам ссылку для регистрации в проекте.

        Аргументы:
            email (EmailStr): email получателя
            url (str): ссылка для регистрации
            name (str): имя получателя
        """
        template_body = {"url": url, "name": name}
        recipients = []
        recipients.append(email)
        email_obj = EmailSchema(recipients=recipients, template_body=template_body)
        await self.__send_mail(
            email_obj,
            "Приглашение в проект \"Ломая Барьеры\"",
            "send_invitation_link.html",
        )
