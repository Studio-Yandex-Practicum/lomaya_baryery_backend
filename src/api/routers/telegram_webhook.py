from typing import Iterator

from fastapi import APIRouter, Request, status
from fastapi.responses import StreamingResponse
from telegram import Update

from src.core.exceptions import UnauthorizedException
from src.core.settings import settings

router = APIRouter(prefix="/telegram", tags=["Telegram template forms and webhook"])


@router.get(
    "/registration_form",
    status_code=status.HTTP_200_OK,
    summary="Вернуть шаблон формы в телеграм",
    response_description="Предоставить пользователю форму для заполнения",
)
def user_register_form_webhook() -> StreamingResponse:
    """
    Вернуть пользователю в телеграм форму для заполнения персональных данных.

    - **name**: имя пользователя
    - **surname**: фамилия пользователя
    - **date_of_birth**: день рождения пользователя
    - **city**: город пользователя
    - **phone_number**: телефон пользователя
    """
    headers: dict[str, str] = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }

    def get_register_form() -> Iterator[bytes]:
        """
        Открывает для чтения html-шаблон формы регистрации пользователя.

        Возвращает генератор для последующего рендеринга шаблона StreamingResponse-ом.
        """
        with open(settings.registration_template, 'rb') as html_form:
            yield from html_form

    return StreamingResponse(get_register_form(), media_type="text/html", headers=headers)


@router.post(
    "/inline_registration_data",
    summary="Получить регистрационные данные пользователя telegram, переданные с inline/menu кнопки",
    response_description="Данные получены",
)
async def get_web_app_query_data(request: Request) -> None:
    """Получение регистрационных данных от пользователя telegram, переданных с inline/menu кнопки.

    Note: адрес данного эндпоинта указан вручную в html-шаблоне страницы регистрации!
    """
    bot_instance = request.app.state.bot_instance
    request_data = await request.json()
    await bot_instance.update_queue.put(request_data)


if settings.BOT_WEBHOOK_MODE:

    @router.post(
        "/webhook",
        summary="Получить обновления telegram",
        response_description="Обновления получены",
    )
    async def get_telegram_bot_updates(request: Request) -> None:
        """Получение обновлений telegram в режиме работы бота webhook."""
        secret_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        if secret_token != settings.SECRET_KEY:
            raise UnauthorizedException
        bot_instance = request.app.state.bot_instance
        request_json_data = await request.json()
        await bot_instance.update_queue.put(Update.de_json(data=request_json_data, bot=bot_instance.bot))
