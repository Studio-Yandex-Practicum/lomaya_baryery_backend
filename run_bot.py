from src.main import create_bot, get_bot_webhook_settings

from src.core.settings import settings

if __name__ == '__main__':
    if settings.BOT_WEBHOOK_MODE:
        webhook_settings = get_bot_webhook_settings()
        create_bot().run_webhook(**webhook_settings)
    else:
        create_bot().run_polling()
