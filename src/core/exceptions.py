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


class ShiftStartForbiddenException(ApplicationException):
    def __init__(self, shift_name: str, shift_id: UUID):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = f"Невозможно начать смену {shift_name} с id: {shift_id}. Проверьте статус смены"


class ShiftFinishForbiddenException(ApplicationException):
    def __init__(self, shift_name: str, shift_id: UUID):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = f"Невозможно завершить смену {shift_name} с id: {shift_id}. Проверьте статус смены"


class SendTelegramNotifyException(ApplicationException):
    """Невозможно отправить сообщение в telegram."""

    def __init__(self, user_id: UUID, user_name: str, telegram_id: int):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = (
            "Ошибка при отправке сообщения пользователю - "
            f"id: {user_id}, name: {user_name}, telegram_id: {telegram_id}. "
            "Пожалуйста, проверьте, что пользователь с таким telegram_id доступен в telegram."
        )
