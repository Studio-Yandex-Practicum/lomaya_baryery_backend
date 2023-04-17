from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse

DEFAULT_ERROR_MESSAGES = {
    HTTPStatus.INTERNAL_SERVER_ERROR: "Ой! У нас что-то сломалось. Но мы обязательно всё починим!",
}


async def internal_exception_handler(request: Request, exc: Exception):
    """Handle 500th error."""
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={"detail": DEFAULT_ERROR_MESSAGES.get(HTTPStatus.INTERNAL_SERVER_ERROR)},
    )


async def application_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle ApplicationError."""
    status_code = getattr(exc, "status_code", None)
    error_message = getattr(exc, "detail", None)

    if status_code is None or error_message is None:
        return await internal_exception_handler(request, exc)

    return JSONResponse(status_code=status_code, content={"detail": error_message})
