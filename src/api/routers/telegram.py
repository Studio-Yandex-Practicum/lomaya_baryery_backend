from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

from src.core.settings import settings

router = APIRouter(prefix="/telegram", tags=["Telegram template forms"])

FORM_AUTOFILL_TELEGRAM_TEMPLATE = "registration.html"


@router.get(
    "/register_form",
    status_code=status.HTTP_200_OK,
    summary="Получить шаблон формы в телеграм",
    response_description="Предоставляет пользователю форму для заполнения",
)
async def user_register_form_webhook():
    """
    Предоставить пользователю в телеграм форму для заполнения
    следующих данных:
    - **name**: имя пользователя
    - **surname**: фамилия пользователя
    - **date_of_birth**: день рождения пользователя
    - **city**: город пользователя
    - **phone_number**: телефон пользователя
    """
    def get_register_form():
        with open(
            settings.registration_template_directory.joinpath(
                FORM_AUTOFILL_TELEGRAM_TEMPLATE
            ), 'rb'
        ) as html_form:
            yield from html_form

    return StreamingResponse(get_register_form(), media_type="text/html")
