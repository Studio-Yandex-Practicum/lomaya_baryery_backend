from fastapi import APIRouter

router = APIRouter()


@router.get("/hello")
async def hello():
    return {"answer": "hello world!"}
