from fastapi import FastAPI

from src.api.routers.v1.views import router_v1

app = FastAPI()
app.include_router(router_v1)


