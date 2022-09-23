import uvicorn

from src.application import create_app
from src.api.routers import router, webhook_router
from src.core.settings import settings

APP_ROUTERS = [router]

if settings.BOT_WEBHOOK_MODE:
    APP_ROUTERS.append(webhook_router)

app = create_app(routers=APP_ROUTERS)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)
