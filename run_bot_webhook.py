import uvicorn

from src.application import create_app
from src.api.routers import webhook_router


app = create_app(routers=[webhook_router],
                 bot_webhook_mode=True)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)
