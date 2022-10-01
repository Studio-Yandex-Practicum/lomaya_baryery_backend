from src.api.request_models.registration import RequestCreate
from src.api.request_models.user import UserCreate
from src.core.db.models import User
from src.core.db.repository.request_repository import RequestRepository
from src.core.db.repository.user_repository import UserRepository

user_repository = UserRepository()
request_repository = RequestRepository


async def user_registration_callback(user_data):
    """Регистрация пользователя."""
    telegram_id = user_data.get("telegram_id")
    user = await user_repository.get_by_attribute("telegram_id", telegram_id)
    if not user:
        user_scheme = UserCreate(**user_data)
        user = User(**user_scheme.dict())
        await user_repository.create(user)
    request = await request_repository.get_by_attribute("id", user.id)
    if not request:
        request_scheme = RequestCreate(user_id=user.id)
        request = User(**request_scheme.dict())
        await request_repository.create(request)
