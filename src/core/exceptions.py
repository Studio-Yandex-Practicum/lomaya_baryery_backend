from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Dict
from uuid import UUID

from starlette.exceptions import HTTPException

from src.core.settings import settings

if TYPE_CHECKING:
    from src.core.db.models import Base as DatabaseModel


class ApplicationError(Exception):
    """Собственное исключение для бизнес-логики приложения."""

    pass


class NotFoundError(ApplicationError):
    status_code: HTTPStatus = HTTPStatus.NOT_FOUND


class BadRequestError(ApplicationError):
    status_code = HTTPStatus.BAD_REQUEST


class ForbiddenError(ApplicationError):
    status_code = HTTPStatus.FORBIDDEN


class UnauthorizedError(ApplicationError):
    status_code = HTTPStatus.UNAUTHORIZED


class NotValidValueError(ApplicationError):
    """Исключение для невалидных данных."""

    def __init__(self, detail: str | None) -> None:
        self.detail = detail
        super().__init__()


class ApplicationException(HTTPException):
    status_code: int = None
    detail: str = None
    headers: Dict[str, Any] = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail, headers=self.headers)


class NotFoundException(NotFoundError):
    def __init__(self, object_name: str, object_id: UUID):
        self.detail = "Объект {} с id: {} не найден".format(object_name, object_id)


class AlreadyExistsException(BadRequestError):
    def __init__(self, obj: DatabaseModel):
        self.detail = f"Объект {obj} уже существует"


class CurrentTaskNotFoundError(ApplicationError):
    """Не найдено текущей задачи для пользователя."""

    detail = "Сейчас заданий нет."


class TodayTaskNotFoundError(ApplicationError):
    """Не найдено ежедневной задачи на текущий день."""

    detail = "На сегодня заданий больше нет."


class CannotAcceptReportError(ApplicationError):
    """Статус задания пользователя не позволяет выполнить операцию."""

    detail = "Ранее отправленный отчет проверяется или уже принят. Новые отчеты сейчас не принимаются."


class DuplicateReportError(ApplicationError):
    """Отчет с таким фото уже отправлялся ранее."""

    detail = "Данная фотография уже использовалась в другом отчёте. Пожалуйста, загрузите другую фотографию."


class ExceededAttemptsReportError(ApplicationError):
    """Превышено количество попыток сдать отчет."""

    detail = (
        "Превышено количество попыток сдать отчет."
        "Предлагаем продолжить, ведь впереди много интересных заданий. "
        f"Следующее задание придет в {settings.formatted_task_time} часов утра."
    )


class EmptyReportError(ApplicationError):
    """Отчет должен содержать фото."""

    detail = "Отчет должен содержать фото."


class ReportSkippedError(ApplicationError):
    """Отчет пропущен."""

    detail = f"Задание было пропущено, следующее задание придет в {settings.formatted_task_time} часов утра."


class ShiftStartForbiddenException(BadRequestError):
    def __init__(self, shift_name: str, shift_id: UUID):
        self.detail = f"Невозможно начать смену {shift_name} с id: {shift_id}. Проверьте статус смены"


class ShiftFinishForbiddenException(BadRequestError):
    def __init__(self, shift_name: str, shift_id: UUID):
        self.detail = f"Невозможно завершить смену {shift_name} с id: {shift_id}. Проверьте статус смены"


class ShiftCancelForbiddenException(BadRequestError):
    def __init__(self, shift_name: str, shift_id: UUID):
        self.detail = f"Невозможно отменить смену {shift_name} с id: {shift_id}. Проверьте статус смены"


class ReportAlreadyReviewedException(ApplicationException):
    def __init__(self, status: UUID):
        self.detail = "Задание уже проверено, статус задания: {}.".format(status)


class ReportWaitingPhotoException(NotFoundError):
    detail = "К заданию нет отчета участника."


class CreateShiftForbiddenException(ForbiddenError):
    def __init__(self, detail: str):
        self.detail = detail


class ShiftUpdateException(BadRequestError):
    def __init__(self, detail: str):
        self.detail = detail


class UpdateShiftForbiddenException(ForbiddenError):
    def __init__(self, detail: str):
        self.detail = detail


class ShiftsDatesIntersectionException(BadRequestError):
    detail = "Дата окончания текущей смены не может равняться или быть больше даты начала новой смены"


class GetStartedShiftException(NotFoundError):
    def __init__(self, detail: str):
        self.detail = detail


class RegistrationForbidenException(ForbiddenError):  # noqa N818
    detail = (
        "К сожалению, на данный момент мы не можем зарегистрировать вас в проекте: смена уже "
        "началась и группа участников набрана. Чтобы не пропустить актуальные новости "
        "Центра \"Ломая барьеры\" - вступайте в нашу группу ВКонтакте https://vk.com/socialrb02"
    )


class AlreadyRegisteredException(ForbiddenError):  # noqa N818
    detail = (
        "Вы уже зарегистрированы в проекте, ожидайте свое первое задание "
        "в день старта смены. Актуальную дату начала смены вы можете "
        "посмотреть в нашей группе ВКонтакте https://vk.com/socialrb02"
    )


class RequestAlreadyReviewedException(ForbiddenError):
    def __init__(self, status):
        self.detail = "Заявка на участие уже проверена, статус заявки: {}.".format(status)


class RequestForbiddenException(ForbiddenError):  # noqa N818
    detail = (
        "К сожалению, на данный момент мы не можем зарегистрировать вас на текущую смену. "
        "Чтобы не пропустить актуальные новости Центра \"Ломая барьеры\" - вступайте "
        "в нашу группу ВКонтакте https://vk.com/socialrb02"
    )


class InvalidAuthenticationDataException(BadRequestError):
    """Введены неверные данные для аутентификации."""

    detail = "Неверный email или пароль."


class AdministratorBlockedException(ForbiddenError):
    """Попытка аутентификации заблокированного пользователя."""

    detail = "Пользователь заблокирован."


class UnauthorizedException(UnauthorizedError):
    """Пользователь не авторизован."""

    detail = "У Вас нет прав для просмотра запрошенной страницы."


class AdministratorNotFoundException(BadRequestError):
    """Пользователь не найден."""

    detail = "Пользователь с указанными реквизитами не найден."


class AdministratorAlreadyExistsException(BadRequestError):
    """Пользователь с таким email уже существует."""

    detail = "Администратор с указанным email уже существует."


class AdministratorInvitationInvalid(BadRequestError):  # noqa N818
    detail = "Указанный код регистрации неверен или устарел."


class EmailSendException(BadRequestError):
    def __init__(self, recipients: list[str], exc: Exception):
        self.detail = f"Возникла ошибка {exc} при отправке email на адрес {recipients}."


class InvalidDateFormatException(BadRequestError):
    detail = "Некорректный формат даты. Ожидаемый формат: YYYY-MM-DD."


class InvitationAlreadyDeactivated(ForbiddenError):
    detail = "Приглашение уже деактивировано"


class InvitationAlreadyActivated(ForbiddenError):
    detail = "Приглашение активно"


class AdministratorChangeError(ForbiddenError):
    detail = "У вас нет прав на изменение других администраторов."


class AdministratorSelfChangeRoleError(ForbiddenError):
    detail = "Вы не можете изменить роль самому себе."


class AdministratorBlockError(ForbiddenError):
    detail = "У Вас нет прав на блокировку других администраторов."


class AdministratorSelfBlockError(ForbiddenError):
    detail = "Вы не можете заблокировать себя."
