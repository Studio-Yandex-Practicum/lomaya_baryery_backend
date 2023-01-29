from fastapi import APIRouter, Depends, Request, status

from src.api.request_models.user import UserWebhookTelegram
from src.core.settings import settings

router = APIRouter(prefix="/telegram", tags=["Telegram template forms"])

FORM_AUTOFILL_TELEGRAM_TEMPLATE = "registration.html"


@router.get(
    "/register_form",
    status_code=status.HTTP_200_OK,
    summary="Получить шаблон формы в телеграм",
    response_description="Заполняет форму пользоваптельскими данными",
)
async def user_register_form_webhook(request: Request, webhook_telegram_user: UserWebhookTelegram = Depends()):
    """
    Получить форму пользователя в телеграм.

    - **UserWebhookTelegram**: входящая Query-форма
    - **name**: имя пользователя
    - **surname**: фамилия пользователя
    - **date_of_birth**: день рождения пользователя
    - **city**: город пользователя
    - **phone_number**: телефон пользователя
    """
    income_user_form = webhook_telegram_user.dict()
    context = dict(request=request)
    if all(income_user_form.values()):
        context.update(income_user_form)
    return settings.TEMPLATES.TemplateResponse(FORM_AUTOFILL_TELEGRAM_TEMPLATE, context=context)
