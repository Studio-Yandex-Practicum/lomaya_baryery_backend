import uvicorn

from fastapi import FastAPI, Request
from telegram import Update

from src.main import start_bot, create_bot


app = FastAPI()


@app.on_event("startup")
async def on_startup():
    """Действия при запуске сервера с ботом."""
    bot_app = await start_bot(webhook_mode=True)
    app.state.bot_app = bot_app


@app.on_event('shutdown')
async def on_shutdown():
    """Действия после остановки сервера с ботом."""
    bot_app = create_bot()
    await bot_app.shutdown()


@app.post('/telegram_handler')
async def get_telegram_bot_updates(request: Request) -> dict:
    """Получение обновлений telegram в режиме работы бота webhook."""
    bot_app = request.app.state.bot_app
    request_json_data = await request.json()
    await bot_app.update_queue.put(
        Update.de_json(data=request_json_data, bot=bot_app.bot)
    )
    return request_json_data


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)
