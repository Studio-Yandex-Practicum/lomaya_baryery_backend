from telegram import Bot

from src.main import create_bot
from src.core.settings import ORGANIZATIONS_EMAIL, ORGANIZATIONS_GROUP


APPROVAL_MESSAGE = (
    'Привет, {first_name} {second_name} пользователя!'
    'Поздравляем, ты в проекте!'
)
REJECTION_MESSAGE = (
    f'К сожалению, на данный момент мы не можем зарегистрировать вас в '
    f'проекте. Вы можете написать на почту {ORGANIZATIONS_EMAIL}. Чтобы не '
    'пропустить актуальные новости Центра "Ломая барьеры" - вступайте '
    f'в нашу группу {ORGANIZATIONS_GROUP}'
)

bot = create_bot().bot  # временная копия бота до миграции на webhooks


class VerificationNotification:
    """Класс для отправки уведомления пользователю
    о результате проверки его заявки на участие в проекте"""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_approval_callback(self, id, first_name, second_name):
        await self.bot.send_message(
            chat_id=id,
            text=APPROVAL_MESSAGE.format(
                first_name=first_name,
                second_name=second_name
            )
        )

    async def send_rejection_callback(self, id):
        await self.bot.send_message(
            chat_id=id,
            text=REJECTION_MESSAGE
        )
