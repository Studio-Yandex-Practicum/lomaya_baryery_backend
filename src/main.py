from fastapi import FastAPI

from src.api.routers import router
from src.core.db.db import init_db

app = FastAPI()

app.include_router(router)


# @app.on_event("startup")
async def on_startup():
    await init_db()
