from telegram import Bot

from src.main import create_bot


APPROVAL_MESSAGE = (
    'Привет, {first_name} {second_name} пользователя!'
    'Поздравляем, ты в проекте!'
)
REJECTION_MESSAGE = (
    'К сожалению, на данный момент мы не можем зарегистрировать вас в '
    'проекте. Вы можете написать на почту info@stereotipov.net. Чтобы не '
    'пропустить актуальные новости Центра "Ломая барьеры" - вступайте '
    'в нашу группу https://vk.com/socialrb02'
)

bot = create_bot().bot  # временная копия бота до миграции на webhooks


class VerificationNotification:

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
