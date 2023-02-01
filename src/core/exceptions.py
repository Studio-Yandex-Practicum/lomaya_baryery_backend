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
        self.detail = f"Объект {object_name} с id: {object_id} не найден"


class CurrentTaskNotFoundError(Exception):
    """Не найдено текущей задачи для пользователя."""


class TodayTaskNotFoundError(Exception):
    """Не найдено ежедневной задачи на текущий день."""


class CannotAcceptReportError(Exception):
    """Статус задания пользователя не позволяет выполнить операцию."""


class DuplicateReportError(Exception):
    """Отчет с таким фото уже отправлялся ранее."""


class ExceededAttemptsReportError(Exception):
    """Превышено количество попыток сдать отчет."""


class EmptyReportError(Exception):
    """Отчет должен содержать фото."""


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

    def __init__(self, user_id: UUID, user_name: str, surname: str, telegram_id: int, exc: Exception):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = (
            f"Возникла ошибка '{exc}' при отправке сообщения пользователю -"
            f" id: {user_id}, Имя: {user_name}, Фамилия: {surname}, Телеграм id: {telegram_id}"
        )


class ReportAlreadyReviewedException(ApplicationException):
    def __init__(self, status: UUID):
        self.status_code = HTTPStatus.FORBIDDEN
        self.detail = f"Задание уже проверено, статус задания: {status}."


class ReportWaitingPhotoException(ApplicationException):
    def __init__(self):
        self.status_code = HTTPStatus.NOT_FOUND
        self.detail = "К заданию нет отчета участника."


class ShiftCreateException(ApplicationException):
    def __init__(self):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = "Запрещено создавать более одной новой смены"


class ShiftUpdateException(ApplicationException):
    def __init__(self, detail: str):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = detail


class ShiftsDatesIntersectionException(ApplicationException):
    def __init__(self):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = "Дата окончания текущей смены не может равняться или быть больше даты начала новой смены"


class GetStartedShiftException(ApplicationException):
    def __init__(self, detail: str):
        self.status_code = HTTPStatus.NOT_FOUND
        self.detail = detail


class RegistrationException(HTTPException):
    status_code: int = None
    detail: str = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class RegistrationForbidenException(RegistrationException):
    def __init__(self):
        self.status_code = HTTPStatus.FORBIDDEN
        self.detail = (
            "К сожалению, на данный момент мы не можем зарегистрировать вас в проекте: смена уже "
            "началась и группа участников набрана. Чтобы не пропустить актуальные новости "
            "Центра \"Ломая барьеры\" - вступайте в нашу группу ВКонтакте https://vk.com/socialrb02"
        )


class AlreadyRegisteredException(RegistrationException):
    def __init__(self):
        self.status_code = HTTPStatus.OK
        self.detail = (
            "Вы уже зарегестрированы в проекте, ожидайте свое первое задание "
            "в день старта смены. Актуальную дату начала смены вы можете "
            "посмотреть в нашей группе ВКонтакте https://vk.com/socialrb02"
        )


class RequestAlreadyReviewedException(ApplicationException):
    def __init__(self, status):
        self.status_code = HTTPStatus.FORBIDDEN
        self.detail = f"Заявка на участие уже проверена, статус заявки: {status}."


class RequestForbiddenException(RegistrationException):
    def __init__(self):
        self.status_code = HTTPStatus.FORBIDDEN
        self.detail = (
            "К сожалению, на данный момент мы не можем зарегистрировать вас на текущую смену. "
            "Чтобы не пропустить актуальные новости Центра \"Ломая барьеры\" - вступайте "
            "в нашу группу ВКонтакте https://vk.com/socialrb02"
        )


class InvalidAuthenticationDataException(ApplicationException):
    """Введены неверные данные для аутентификации."""

    status_code = HTTPStatus.BAD_REQUEST
    detail = "Неверный email или пароль."


class AdministratorBlockedException(ApplicationException):
    """Попытка аутентификации заблокированного пользователя."""

    status_code = HTTPStatus.FORBIDDEN
    detail = "Пользователь заблокирован."


class UnauthorizedException(ApplicationException):
    """Пользователь не авторизован."""

    status_code = HTTPStatus.UNAUTHORIZED
    detail = "У Вас нет прав для просмотра запрошенной страницы."


class AdministratorNotFoundException(ApplicationException):
    """Пользователь не найден."""

    status_code = HTTPStatus.BAD_REQUEST
    detail = "Пользователь с указанными реквизитами не найден."


class AdministratorInvitationInvalid(RegistrationException):
    def __init__(self):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = "Указанный код регистрации неверен или устарел."


class EmailSendException(ApplicationException):
    def __init__(self, recipients: list[str], exc: Exception):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = f"Возникла ошибка {exc} при отправке email на адрес {recipients}."
