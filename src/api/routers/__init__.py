from src.api.routers.excel_report import router as excel_router  # noqa
from src.api.routers.healthcheck import router as healthcheck_router  # noqa
from src.api.routers.hello import (  # noqa
    TELEGRAM_WEBHOOK_ENDPOINT,
    router,
    webhook_router,
)
from src.api.routers.report import router as report_router  # noqa
from src.api.routers.request import router as request_router  # noqa
from src.api.routers.shift import router as shift_router  # noqa
from src.api.routers.task import router as task_router  # noqa
from src.api.routers.user import router as user_router  # noqa
