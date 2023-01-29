from http import HTTPStatus
from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


def generate_error_responses(*error_status_codes: int) -> dict[int, dict[str, Any]]:
    """Создает шаблоны ошибок из входящих статус кодов."""
    return {code: {"description": HTTPStatus(code).phrase, "model": ErrorResponse} for code in error_status_codes}
