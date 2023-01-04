from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.routers import (
    healthcheck_router,
    report_router,
    request_router,
    router,
    shift_router,
    user_router,
    webhook_router,
)
from src.bot.main import start_bot
from src.core.exceptions import NotFoundException
from src.core.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(debug=settings.DEBUG, docs_url="/dd")

    origins = ["*"]

    # для локального тестирования монтируем статику
    app.mount("/static", StaticFiles(directory="src/static"), name="static")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    app.include_router(report_router)
    app.include_router(shift_router)
    app.include_router(request_router)
    app.include_router(healthcheck_router)
    app.include_router(user_router)
    if settings.BOT_WEBHOOK_MODE:
        app.include_router(webhook_router)

    @app.on_event("startup")
    async def on_startup():
        """Действия при запуске сервера."""
        bot_instance = await start_bot()
        # storing bot_instance to extra state of FastAPI app instance
        # refer to https://www.starlette.io/applications/#storing-state-on-the-app-instance
        app.state.bot_instance = bot_instance

    @app.exception_handler(NotFoundException)
    async def invalid_db_request(request: Request, exc: NotFoundException):
        return JSONResponse(status_code=exc.status_code, content=jsonable_encoder({exc.detail: exc.status_code}))

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
