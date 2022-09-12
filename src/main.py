import telebot
from fastapi import FastAPI

from src.api.routers.v1.views import router_v1
from src.core.settings import BOT_TOKEN

app = FastAPI()
app.include_router(router_v1)


