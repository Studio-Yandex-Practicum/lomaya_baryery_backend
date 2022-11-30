from http import HTTPStatus
from typing import Any, Dict
from uuid import UUID

from starlette.exceptions import HTTPException


class ApplicationException(HTTPException):
    status_code: int = None
    detail: str = None
    headers: Dict[str, Any] = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail, headers=self.headers)


class NotFoundException(ApplicationException):
    def __init__(self, object_name: str, object_id: UUID):
        self.status_code = HTTPStatus.NOT_FOUND
        self.detail = "Объект {} с id: {} не найден".format(object_name, object_id)


class CurrentTaskNotFoundError(Exception):
    """Не найдено текущей задачи для пользователя."""

    pass


class CannotAcceptReportError(Exception):
    """Статус задания пользователя не позволяет выполнить операцию."""

    pass


class DuplicateReportError(Exception):
    """Отчет с таким фото уже отправлялся ранее."""

    pass
