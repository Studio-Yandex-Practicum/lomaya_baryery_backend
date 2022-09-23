from fastapi import APIRouter

from src.api.routers import hello, user_tasks


main_router = APIRouter()
main_router.include_router(hello)
main_router.include_router(user_tasks)