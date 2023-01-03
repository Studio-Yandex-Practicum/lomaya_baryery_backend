from fastapi import APIRouter, Depends, Request, status
from fastapi.templating import Jinja2Templates

from src.api.request_models.user import UserWebhookTelegram
from src.core.settings import BASE_DIR

templates = Jinja2Templates(directory=BASE_DIR / "src" / "static")
router = APIRouter(prefix="/telegram", tags=["Telegram template forms"])


@router.get(
    "/register_form",
    status_code=status.HTTP_200_OK,
    summary="Получить шаблон формы в телеграм",
    response_description="Заполняет форму пользоваптельскими данными",
)
async def user_register_form_webhook(
    request: Request, webhook_telegram_user: UserWebhookTelegram = Depends()
) -> Jinja2Templates:
    """
    Получить форму пользователя в телеграм.

    - **UserWebhookTelegram**: входящая Query-форма
    - **name**: имя пользователя
    - **surname**: фамилия пользователя
    - **date_of_birth**: день рождения пользователя
    - **city**: город пользователя
    - **phone_number**: телефон пользователя
    """
    context = dict(request=request)

    context.update(webhook_telegram_user.dict())
    return templates.TemplateResponse("registration.html", context=context)
