from typing import Iterator

from fastapi import APIRouter, Request, status
from fastapi.responses import StreamingResponse
from telegram import Update

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


if settings.BOT_WEBHOOK_MODE:

    @router.post(
        "/webhook",
        summary="Получить обновления telegram",
        response_description="Обновления получены",
    )
    async def get_telegram_bot_updates(request: Request) -> dict:
        """Получение обновлений telegram в режиме работы бота webhook."""
        bot_instance = request.app.state.bot_instance
        request_json_data = await request.json()
        await bot_instance.update_queue.put(Update.de_json(data=request_json_data, bot=bot_instance.bot))
        return request_json_data
