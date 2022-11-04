from http import HTTPStatus
from typing import Any, Dict

from starlette.exceptions import HTTPException


class ApplicationException(HTTPException):
    status_code: int = None
    detail: str = None
    headers: Dict[str, Any] = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail, headers=self.headers)


class NotFoundException(ApplicationException):
    status_code = HTTPStatus.NOT_FOUND
    detail = 'Запрашиваемый объект не найден'
