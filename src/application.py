from typing import List

from fastapi import FastAPI, APIRouter

from src.core.settings import settings
from src.bot.main import start_bot


def create_app(
    routers: List[APIRouter],
    bot_webhook_mode: bool = settings.BOT_WEBHOOK_MODE
) -> FastAPI:
    app = FastAPI()
    for router in routers:
        app.include_router(router)

    @app.on_event("startup")
    async def on_startup():
        """Действия при запуске сервера."""
        bot_app = await start_bot(bot_webhook_mode)
        # storing bot_app to extra state of FastAPI app instance
        # refer to https://www.starlette.io/applications/#storing-state-on-the-app-instance
        app.state.bot_app = bot_app

    @app.on_event('shutdown')
    async def on_shutdown():
        """Действия после остановки сервера."""
        bot_app = app.state.bot_app
        await bot_app.stop()
        # manually stopping bot updater when running in polling mode
        # see https://github.com/python-telegram-bot/python-telegram-bot/blob/master/telegram/ext/_application.py#L523 # noqa
        if bot_app.updater:
            await bot_app.updater.stop()
        await bot_app.shutdown()

    return app
