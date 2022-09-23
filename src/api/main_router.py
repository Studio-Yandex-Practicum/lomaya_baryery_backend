from fastapi import APIRouter

from src.api.routers import task_router

main_router = APIRouter()


@main_router.get("/hello")
async def hello():
    return {"answer": "hello world!"}

main_router.include_router(
    task_router,
    prefix='/tasks',
    tags=['Tasks']
)
