from fastapi import APIRouter, Request
from telegram import Update


BOT_WEBHOOK_ENDPOINT = '/telegram_webhook'

router = APIRouter()


@router.get("/hello")
async def hello():
    return {"answer": "hello world!"}


@router.post(BOT_WEBHOOK_ENDPOINT)
async def get_telegram_bot_updates(request: Request):
    """Получение обновлений telegram в режиме работы бота webhook."""
    bot_app = request.app.state.bot_app
    request_json_data = await request.json()
    await bot_app.update_queue.put(
        Update.de_json(data=request_json_data, bot=bot_app.bot)
    )
    return request_json_data
