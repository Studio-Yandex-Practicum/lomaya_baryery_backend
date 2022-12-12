from src.api.routers.healthcheck import router as healthcheck_router  # noqa
from src.api.routers.hello import (  # noqa
    TELEGRAM_WEBHOOK_ENDPOINT,
    router,
    webhook_router,
)
from src.api.routers.report import router as report_router  # noqa
from src.api.routers.request import router as request_router  # noqa
from src.api.routers.shift import router as shift_router  # noqa
