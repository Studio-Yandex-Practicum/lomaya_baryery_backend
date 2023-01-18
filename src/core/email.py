from typing import Any

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from src.core.settings import ORGANIZATIONS_EMAIL, settings


class Email:
    """Класс для отправки электронных писем."""

    async def send_mail(
        self,
        recipients: list[EmailStr],
        template_body: dict[str, Any],
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
            recipients=recipients,
            template_body=template_body,
            subtype=MessageType.html,
        )

        fastmail = FastMail(conf)
        await fastmail.send_message(message, template_name)

    async def send_invitation_link(self, recipients: list[EmailStr], url: str, name: str) -> None:
        """Отправляет указанным адресатам ссылку для регистрации в проекте.

        Аргументы:
            recipients (list[EmailStr]): список email получателей
            url (str): ссылка для регистрации
            name (str): имя получателя
        """
        template_body = {"url": url, "name": name}
        await self.send_mail(
            recipients,
            template_body,
            "Приглашение в проект \"Ломая Барьеры\"",
            "send_invitation_link.html",
        )
