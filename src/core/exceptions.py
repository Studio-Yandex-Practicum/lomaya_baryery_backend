from http import HTTPStatus
from typing import Optional
from uuid import UUID

from starlette.exceptions import HTTPException


class ApplicationException(Exception):
    def __init__(self, status_code: int, detail: Optional[str] = None) -> None:
        if detail is None:
            detail = HTTPStatus(status_code).phrase
        self.status_code = status_code
        self.detail = detail


class ObjectNotFoundError(ApplicationException):
    status_code = HTTPStatus.NOT_FOUND

    def __init__(self, object_name: str, object_id: UUID):
        self.detail = f"Объект '{object_name}' с id: {object_id} не найден"


class TaskCurrentNotFoundError(Exception):
    """Не найдено текущей задачи для пользователя."""


class TaskTodayNotFoundError(Exception):
    """Не найдено ежедневной задачи на текущий день."""


class ReportCannotAcceptError(Exception):
    """Статус задания пользователя не позволяет выполнить операцию."""


class ReportDuplicateError(Exception):
    """Отчет с таким фото уже отправлялся ранее."""


class ReportExceededAttemptsError(Exception):
    """Превышено количество попыток сдать отчет."""


class ReportEmptyError(Exception):
    """Отчет должен содержать фото."""


class RequestSendTelegramNotifyError(ApplicationException):
    """Невозможно отправить сообщение в telegram."""

    def __init__(self, user_id: UUID, user_name: str, surname: str, telegram_id: int, exc: Exception):
        self.detail = (
            f"Возникла ошибка '{exc}' при отправке сообщения пользователю -"
            f" id: {user_id}, Имя: {user_name}, Фамилия: {surname}, Телеграм id: {telegram_id}"
        )


class ReportAlreadyReviewedError(ApplicationException):
    def __init__(self, status: str):
        self.detail = f"Задание уже проверено, статус задания: {status}."


class ReportWaitingPhotoError(ApplicationException):
    detail = "К заданию нет отчета участника"


class ShiftStatusError(ApplicationException):
    def __init__(self, shift_name: str, shift_id: UUID):
        self.detail = f"Невозможно начать/завершить смену '{shift_name}' с id: {shift_id}. Проверьте статус смены"


class ShiftCreateError(ApplicationException):
    def __init__(self):
        self.detail = "Запрещено создавать более одной новой смены"


class ShiftDateTodayPastError(ApplicationException):
    def __init__(self):
        self.detail = "Дата начала/окончания смены не может быть сегодняшним или прошедшим числом"


class ShiftDateMaxDurationError(ApplicationException):
    def __init__(self):
        self.detail = "Смена не может длиться больше 4-х месяцев"


class ShiftDateStartFinishError(ApplicationException):
    def __init__(self):
        self.detail = "Дата начала смены не может равняться или быть позже дате окончания"


class ShiftDateIntersectionError(ApplicationException):
    def __init__(self):
        self.detail = "Дата начала новой смены не может равняться или быть раньше даты окончания текущей смены"


class ShiftUpdateError(ApplicationException):
    def __init__(self):
        self.detail = "Запрещено изменять завершенную или отмененную смену"


class ShiftDateUpdateStartError(ApplicationException):
    def __init__(self):
        self.detail = "Запрещено изменять дату начала текущей смены"


class ShiftStartedNotFoundError(ObjectNotFoundError):
    def __init__(self):
        self.detail = "Активной смены не найдено"


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
            "Вы уже зарегистрированы в проекте, ожидайте свое первое задание "
            "в день старта смены. Актуальную дату начала смены вы можете "
            "посмотреть в нашей группе ВКонтакте https://vk.com/socialrb02"
        )


class RequestAlreadyReviewedError(ApplicationException):
    def __init__(self, status):
        self.detail = f"Заявка на участие уже проверена, статус заявки: {status}."


class RequestForbiddenError(RegistrationException):
    def __init__(self):
        self.status_code = HTTPStatus.FORBIDDEN
        self.detail = (
            "К сожалению, на данный момент мы не можем зарегистрировать вас на текущую смену. "
            "Чтобы не пропустить актуальные новости Центра \"Ломая барьеры\" - вступайте "
            "в нашу группу ВКонтакте https://vk.com/socialrb02"
        )


class InvalidAuthenticationError(ApplicationException):
    """Введены неверные данные для аутентификации."""

    def __init__(self):
        self.detail = "Неверный email или пароль"


class AdministratorBlockedError(ApplicationException):
    """Попытка аутентификации заблокированного пользователя."""

    def __init__(self):
        self.status_code = HTTPStatus.FORBIDDEN
        self.detail = "Пользователь заблокирован"


class UnauthorizedError(ApplicationException):
    """Пользователь не авторизован."""

    def __init__(self):
        self.status_code = HTTPStatus.UNAUTHORIZED
        self.detail = "У Вас нет прав для просмотра запрошенной страницы"


class AdministratorInvitationInvalidError(RegistrationException):
    def __init__(self):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = "Указанный код регистрации неверен или устарел."


class EmailSendError(ApplicationException):
    def __init__(self, recipients: list[str], exc: Exception):
        self.detail = f"Возникла ошибка {exc} при отправке email на адрес {recipients}."
