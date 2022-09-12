from fastapi import APIRouter

router = APIRouter()


@router.post("/hello")
async def hello():
    return {"answer": "hello world!"}
