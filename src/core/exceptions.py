from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from uuid import UUID

from src.core.settings import settings

if TYPE_CHECKING:
    from src.core.db.models import Base as DatabaseModel
    from src.core.db.models import Request, Shift


class ApplicationError(Exception):
    """Собственное исключение для бизнес-логики приложения."""

    detail: str = "О! Какая-то неопознанная ошибка. Мы её обязательно опознаем и исправим!"



class NotFoundError(ApplicationError):
    status_code: HTTPStatus = HTTPStatus.NOT_FOUND


class BadRequestError(ApplicationError):
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST


class UnauthorizedError(ApplicationError):
    status_code: HTTPStatus = HTTPStatus.UNAUTHORIZED


class NotValidValueError(ApplicationError):
    """Исключение для невалидных данных."""

    def __int__(self, detail: str) -> None:
        self.detail = detail


class ObjectNotFoundError(NotFoundError):
    def __init__(self, model: DatabaseModel, object_id: UUID):
        self.detail = "Объект '{}' с id '{}' не найден".format(model.__name__, object_id)


class ObjectAlreadyExistsError(BadRequestError):
    def __init__(self, model: DatabaseModel):
        self.detail = "Объект {} уже существует".format(model)


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
        "Следующее задание придет в {} часов утра.".format(settings.formatted_task_time)
    )


class EmptyReportError(ApplicationError):
    """Отчет должен содержать фото."""

    detail = "Отчет должен содержать фото."


class ReportSkippedError(ApplicationError):
    """Отчет пропущен."""

    detail = "Задание было пропущено, следующее задание придет в {} часов утра.".format(settings.formatted_task_time)


class ShiftStartError(BadRequestError):
    def __init__(self, shift: Shift):
        self.detail = "Невозможно начать смену {} с id: {}. Проверьте статус смены".format(shift.title, shift.id)


class ShiftReadyForCompleteForbiddenException(BadRequestError):
    def __init__(self, shift_name: str, shift_id: UUID):
        self.detail = (
            f"Невозможно перевести в статус 'завершающаяся' смену {shift_name} с id: {shift_id}. Проверьте статус смены"
        )


class ShiftReadyForCompleteForbiddenException(BadRequestError):
    def __init__(self, shift_name: str, shift_id: UUID):
        self.detail = (
            f"Невозможно перевести в статус 'завершающаяся' смену {shift_name} с id: {shift_id}. Проверьте статус смены"
        )


class ShiftFinishError(BadRequestError):
    def __init__(self, shift: Shift):
        self.detail = "Невозможно завершить смену {} с id: {}. Проверьте статус смены".format(shift.title, shift.id)


class ShiftCancelError(BadRequestError):
    def __init__(self, shift: Shift):
        self.detail = "Невозможно отменить смену {} с id: {}. Проверьте статус смены".format(shift.title, shift.id)


class ShiftError(BadRequestError):
    def __int__(self, detail: str) -> None:
        self.detail = detail


class ShiftsDatesIntersectionError(BadRequestError):
    detail = "Дата окончания текущей смены не может равняться или быть больше даты начала новой смены"


class ShiftNotFoundError(NotFoundError):
    detail = "Активной смены не найдено."


class ReportAlreadyReviewedError(BadRequestError):
    def __init__(self, status: Report.Status):
        self.detail = "Задание уже проверено, статус задания: {}.".format(status)


class ReportWaitingPhotoError(NotFoundError):
    detail = "К заданию нет отчета участника."


class RegistrationForbiddenError(BadRequestError):
    detail = (
        "К сожалению, на данный момент мы не можем зарегистрировать вас в проекте: смена уже "
        "началась и группа участников набрана. Чтобы не пропустить актуальные новости "
        "Центра \"Ломая барьеры\" - вступайте в нашу группу ВКонтакте {}".format(settings.ORGANIZATIONS_GROUP)
    )


class AlreadyRegisteredError(BadRequestError):
    detail = (
        "Вы уже зарегистрированы в проекте, ожидайте свое первое задание "
        "в день старта смены. Актуальную дату начала смены вы можете "
        "посмотреть в нашей группе ВКонтакте {}".format(settings.ORGANIZATIONS_GROUP)
    )


class RequestAlreadyReviewedError(BadRequestError):
    def __init__(self, status: Request.Status):
        self.detail = "Заявка на участие уже проверена, статус заявки: {}.".format(status)


class RequestForbiddenError(BadRequestError):
    detail = (
        "К сожалению, на данный момент мы не можем зарегистрировать вас на текущую смену. "
        "Чтобы не пропустить актуальные новости Центра \"Ломая барьеры\" - вступайте "
        "в нашу группу ВКонтакте {}".format(settings.ORGANIZATIONS_GROUP)
    )


class InvalidAuthenticationDataError(BadRequestError):
    """Введены неверные данные для аутентификации."""

    detail = "Неверный email или пароль."


class AdministratorBlockedError(BadRequestError):
    """Попытка аутентификации заблокированного пользователя."""

    detail = "Пользователь заблокирован."


class AdministratorNotFoundError(BadRequestError):
    """Пользователь не найден."""

    status_code = HTTPStatus.NOT_FOUND
    detail = "Пользователь с указанными реквизитами не найден."


class AdministratorAlreadyExistsError(BadRequestError):
    """Пользователь с таким email уже существует."""

    detail = "Администратор с указанным email уже существует."


class AdministratorInvitationInvalidError(BadRequestError):
    detail = "Указанный код регистрации неверен или устарел."


class EmailSendError(BadRequestError):
    def __init__(self, recipients: list[str], exc: Exception):
        self.detail = f"Возникла ошибка {exc} при отправке email на адрес {recipients}."


class InvalidDateFormatError(BadRequestError):
    detail = "Некорректный формат даты. Ожидаемый формат: YYYY-MM-DD."


class InvitationAlreadyDeactivatedError(BadRequestError):
    detail = "Приглашение уже деактивировано"


class InvitationAlreadyActivatedError(BadRequestError):
    detail = "Приглашение активно"


class AdministratorChangeError(BadRequestError):
    detail = "У вас нет прав на изменение других администраторов."


class AdministratorSelfChangeRoleError(BadRequestError):
    detail = "Вы не можете изменить роль самому себе."


class AdministratorBlockError(BadRequestError):
    detail = "У Вас нет прав на блокировку других администраторов."


class AdministratorSelfBlockError(BadRequestError):
    detail = "Вы не можете заблокировать себя."
