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


class BadRequestError(ApplicationError):
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST


class UnauthorizedError(ApplicationError):
    status_code: HTTPStatus = HTTPStatus.UNAUTHORIZED
    detail = "У Вас нет прав для просмотра запрошенной страницы."


class ForbiddenError(ApplicationError):
    status_code: HTTPStatus = HTTPStatus.FORBIDDEN


class NotFoundError(ApplicationError):
    status_code: HTTPStatus = HTTPStatus.NOT_FOUND


class NotValidValueError(ApplicationError):
    """Исключение для невалидных данных."""

    def __int__(self, detail: str) -> None:
        self.detail = detail


class ObjectNotFoundError(NotFoundError):
    def __init__(self, model: DatabaseModel, object_id: UUID):
        self.detail = "Объект '{}' с id '{}' не найден".format(model.__name__, object_id)


class ObjectAlreadyExistsError(BadRequestError):
    def __init__(self, model: DatabaseModel):
        self.detail = "Объект {!r} уже существует".format(model)


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


class ReportCantBeSkippedError(BadRequestError):
    detail = "Ранее отправленный отчет проверяется или уже принят, сейчас нельзя пропустить задание."


class ReportAlreadySkippedError(ApplicationError):
    """Отчет пропущен."""

    detail = "Задание было пропущено, следующее задание придет в {} часов утра.".format(settings.formatted_task_time)


class ReportAlreadyReviewedError(BadRequestError):
    detail = "Задание уже проверено."


class ReportWaitingPhotoError(NotFoundError):
    detail = "К заданию нет отчета участника."


class ShiftStartError(BadRequestError):
    def __init__(self, shift: Shift):
        self.detail = "Невозможно начать смену {!r}. Проверьте статус смены".format(shift)


class ShiftFinishError(BadRequestError):
    def __init__(self, shift: Shift):
        self.detail = "Невозможно завершить смену {!r}. Проверьте статус смены".format(shift)


class ShiftCancelError(BadRequestError):
    def __init__(self, shift: Shift):
        self.detail = "Невозможно отменить смену {!r}. Проверьте статус смены".format(shift)


class ShiftError(BadRequestError):
    def __int__(self, detail: str) -> None:
        self.detail = detail


class ShiftPastDateError(BadRequestError):
    detail = "Нельзя установить дату начала/окончания смены сегодняшним или прошедшим числом"


class ShiftTooShortError(BadRequestError):
    detail = "Дата начала смены не может быть позже или равняться дате окончания"


class ShiftTooLongError(BadRequestError):
    detail = "Смена не может длиться больше 4-х месяцев"


class ChangeCompletedShiftError(BadRequestError):
    detail = "Нельзя изменить завершенную или отмененную смену"


class ShiftCreatedTooFastError(BadRequestError):
    detail = (
        f"Запрещено создавать новую смену, "
        f"если текущая смена запущена менее {settings.DAYS_FROM_START_OF_SHIFT_TO_JOIN} дней назад"
    )


class CurrentShiftChangeDateError(BadRequestError):
    detail = "Нельзя изменить дату начала текущей смены"


class NewShiftExclusiveError(BadRequestError):
    detail = "Запрещено создавать более одной новой смены"


class ShiftsDatesIntersectionError(BadRequestError):
    detail = "Дата окончания текущей смены не может равняться или быть больше даты начала новой смены"


class ShiftNotFoundError(NotFoundError):
    detail = "Активной смены не найдено."


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


class AdministratorBlockedError(ForbiddenError):
    """Попытка аутентификации заблокированного пользователя."""

    detail = "Администратор заблокирован."


class AdministratorNotFoundError(NotFoundError):
    detail = "Администратор с указанными реквизитами не найден."


class AdministratorAlreadyExistsError(BadRequestError):
    detail = "Администратор с указанным email уже существует."


class AdministratorInvitationInvalidError(BadRequestError):
    detail = "Указанный код регистрации неверен или устарел."


class EmailSendError(BadRequestError):
    def __init__(self, recipients: list[str], exc: Exception):
        self.detail = f"Возникла ошибка {exc} при отправке email на адрес {recipients}."


class InvalidDateFormatError(BadRequestError):
    detail = "Некорректный формат даты. Ожидаемый формат: YYYY-MM-DD."


class InvitationAlreadyDeactivatedError(BadRequestError):
    detail = "Невозможно изменить состояние приглашения. Приглашение уже деактивировано."


class ShiftTitleToShortError(BadRequestError):
    def __init__(self):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = "Нельзя создавать/изменять название смены из пробелов."


class ShiftTitleLenExceptionError(BadRequestError):
    def __init__(self):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = "Длина названия смены должна быть от 3 до 60 символов."


class InvitationAlreadyActivatedError(BadRequestError):
    detail = "Невозможно изменить состояние приглашения. Приглашение уже активно"


class AdministratorChangeError(ForbiddenError):
    detail = "У вас нет прав на изменение других администраторов."


class AdministratorSelfChangeRoleError(ForbiddenError):
    detail = "Вы не можете изменить роль самому себе."


class AdministratorBlockError(ForbiddenError):
    detail = "У Вас нет прав на блокировку других администраторов."


class AdministratorSelfBlockError(ForbiddenError):
    detail = "Вы не можете заблокировать себя."
