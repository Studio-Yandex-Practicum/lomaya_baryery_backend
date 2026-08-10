from fastapi import APIRouter, Request

from src.core.exceptions import UnauthorizedError
from src.core.settings import settings

router = APIRouter(prefix="/max", tags=["Max messenger webhook"])

if settings.MAX_BOT_WEBHOOK_MODE:

    @router.post(
        "/webhook/{secret}",
        summary="Получить обновления Max",
        response_description="Обновления получены",
    )
    async def get_max_bot_updates(secret: str, request: Request) -> dict:
        """Получение обновлений Max в режиме работы бота webhook.

        У API Max нет аналога секретного заголовка telegram, поэтому
        секрет вебхука передается в пути, зарегистрированном в подписке.
        """
        if secret != settings.SECRET_KEY:
            raise UnauthorizedError
        max_bot = request.app.state.max_bot
        if max_bot is None:
            raise UnauthorizedError
        request_json_data = await request.json()
        await max_bot.handle_update(request_json_data)
        return {}
