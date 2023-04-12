from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse

DEFAULT_ERROR_MESSAGES = {
    HTTPStatus.INTERNAL_SERVER_ERROR: "Ой! У нас что-то сломалось. Но мы обязательно всё починим!",
}


def default_error_message(status_code: HTTPStatus) -> str:
    """Return default error message.

    Default error message gets from DEFAULT_ERROR_MESSAGES dictionary using
    `status_code` as a key. If there is no message for the given `status_code`
    in the dictionary, it returns a message for the 500th error.
    """
    return DEFAULT_ERROR_MESSAGES.get(status_code, None) or DEFAULT_ERROR_MESSAGES.get(HTTPStatus.INTERNAL_SERVER_ERROR)


async def internal_exception_handler(request: Request, exc: Exception):
    """Handle 500th error."""
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={"detail": DEFAULT_ERROR_MESSAGES.get(HTTPStatus.INTERNAL_SERVER_ERROR)},
    )


async def application_error_handler(request: Request, exc: Exception):
    """Handle ApplicationError."""
    status_code = getattr(exc, "status_code", HTTPStatus.INTERNAL_SERVER_ERROR)
    error_message = getattr(exc, "detail", default_error_message(status_code))
    return JSONResponse(status_code=status_code, content={"detail": error_message})
