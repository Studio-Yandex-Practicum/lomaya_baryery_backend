import uvicorn
from fastapi import FastAPI

from src.main import start_bot
from src.api.routers import webhook_router


app = FastAPI()
app.include_router(webhook_router)


@app.on_event("startup")
async def on_startup():
    """Действия при запуске сервера с ботом."""
    bot_app = await start_bot(webhook_mode=True)
    app.state.bot_app = bot_app


@app.on_event('shutdown')
async def on_shutdown():
    """Действия после остановки сервера с ботом."""
    bot_app = app.state.bot_app
    await bot_app.stop()
    await bot_app.shutdown()


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)
