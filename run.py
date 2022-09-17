import uvicorn

from src.core.db.db import init_db
from src.main import app, start_bot, create_bot


@app.on_event("startup")
async def on_startup():
    """Действия при старте API сервера."""
    await start_bot()


@app.on_event('shutdown')
async def on_shutdown():
    """Действия после остановки API сервера."""
    bot_app = create_bot()
    await bot_app.shutdown()


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)
