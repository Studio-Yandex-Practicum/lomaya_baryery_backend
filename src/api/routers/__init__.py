from src.api.routers.healthcheck import router as healthcheck_router  # noqa
from src.api.routers.hello import (  # noqa
    TELEGRAM_WEBHOOK_ENDPOINT,
    router,
    webhook_router,
)
from src.api.routers.registration import router as registration_router  # noqa
from src.api.routers.request import router as request_router  # noqa
from src.api.routers.shift import router as shift_router  # noqa
from src.api.routers.user_tasks import router as user_tasks  # noqa
