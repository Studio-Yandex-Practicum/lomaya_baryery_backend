from http import HTTPStatus

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api import routers
from src.bot.main import start_bot
from src.core.exception_handlers import internal_exception_handler
from src.core.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(debug=settings.DEBUG, root_path=settings.ROOT_PATH)

    origins = ["*"]

    # для локального тестирования монтируем статику
    app.mount("/static", StaticFiles(directory="static"), name="static")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(routers.report_router)
    app.include_router(routers.shift_router)
    app.include_router(routers.request_router)
    app.include_router(routers.healthcheck_router)
    app.include_router(routers.user_router)
    app.include_router(routers.administrator_router)
    app.include_router(routers.task_router)
    app.include_router(routers.administrator_invitation_router)
    app.include_router(routers.telegram)

    app.add_exception_handler(HTTPStatus.INTERNAL_SERVER_ERROR, internal_exception_handler)

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
