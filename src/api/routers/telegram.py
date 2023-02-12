from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

from src.core.settings import settings

router = APIRouter(prefix="/telegram", tags=["Telegram template forms"])

FORM_AUTOFILL_TELEGRAM_TEMPLATE = "registration.html"


def get_register_form():
    """
    Открывает для чтения html-шаблон, в данном случае формы регистрации пользователя.

    Возвращает генератор для последующего рендеринга шаблона StreamingResponse-ом.
    """
    with open(settings.registration_template_directory.joinpath(FORM_AUTOFILL_TELEGRAM_TEMPLATE), 'rb') as html_form:
        yield from html_form


@router.get(
    "/register_form",
    status_code=status.HTTP_200_OK,
    summary="Вернуть шаблон формы в телеграм",
    response_description="Предоставить пользователю форму для заполнения",
)
def user_register_form_webhook():
    """
    Вернуть пользователю в телеграм форму для заполнения персональных данных.

    - **name**: имя пользователя
    - **surname**: фамилия пользователя
    - **date_of_birth**: день рождения пользователя
    - **city**: город пользователя
    - **phone_number**: телефон пользователя
    """
    return StreamingResponse(get_register_form(), media_type="text/html")
