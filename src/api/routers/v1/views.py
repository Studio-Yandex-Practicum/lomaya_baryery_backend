from fastapi import APIRouter

router_v1 = APIRouter()


@router_v1.post("/hello")
async def hello():
    return {"answer": "hello world!"}
