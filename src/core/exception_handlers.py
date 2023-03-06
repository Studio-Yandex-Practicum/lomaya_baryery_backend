from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse

ERROR_MESSAGES = {
    HTTPStatus.INTERNAL_SERVER_ERROR: "Ой! У нас что-то сломалось. Но мы обязательно всё починим!",
}


async def internal_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={"detail": ERROR_MESSAGES.get(HTTPStatus.INTERNAL_SERVER_ERROR)},
    )
