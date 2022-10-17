from fastapi import FastAPI

from src.api.routers import (
    request_router,
    router,
    shift_router,
    user_tasks,
    webhook_router,
    health_router,
)
from src.bot.main import start_bot
from src.core.settings import settings


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    app.include_router(user_tasks)
    app.include_router(shift_router)
    app.include_router(request_router)
    app.include_router(health_router)
    if settings.BOT_WEBHOOK_MODE:
        app.include_router(webhook_router)

    @app.on_event("startup")
    async def on_startup():
        """Действия при запуске сервера."""
        bot_instance = await start_bot()
        # storing bot_instance to extra state of FastAPI app instance
        # refer to https://www.starlette.io/applications/#storing-state-on-the-app-instance
        app.state.bot_instance = bot_instance

    @app.on_event("shutdown")
    async def on_shutdown():
        """Действия после остановки сервера."""
        bot_instance = app.state.bot_instance
        # manually stopping bot updater when running in polling mode
        # see https://github.com/python-telegram-bot/python-telegram-bot/blob/master/telegram/ext/_application.py#L523
        if not settings.BOT_WEBHOOK_MODE:
            await bot_instance.updater.stop()
        await bot_instance.stop()
        await bot_instance.shutdown()

    return app
