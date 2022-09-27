from fastapi import APIRouter, Request
from telegram import Update

router = APIRouter()

webhook_router = APIRouter()
TELEGRAM_WEBHOOK_ENDPOINT = "/telegram_handler"


@router.get("/hello")
async def hello():
    return {"answer": "hello world!"}


@webhook_router.post(TELEGRAM_WEBHOOK_ENDPOINT)
async def get_telegram_bot_updates(request: Request) -> dict:
    """Получение обновлений telegram в режиме работы бота webhook."""
    bot_instance = request.app.state.bot_instance
    request_json_data = await request.json()
    await bot_instance.update_queue.put(Update.de_json(data=request_json_data, bot=bot_instance.bot))
    return request_json_data
