from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Dict
from uuid import UUID

from starlette.exceptions import HTTPException

from src.core.settings import settings

if TYPE_CHECKING:
    from src.core.db.models import Base as DatabaseModel


class ApplicationError(HTTPException):
    """Собственное исключение для бизнес-логики приложения."""

    status_code: int = None
    detail: str = "О! Какая-то неопознанная ошибка. Мы её обязательно опознаем и исправим!"
    headers: Dict[str, Any] = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail, headers=self.headers)



class NotFoundError(ApplicationError):
    status_code: HTTPStatus = HTTPStatus.NOT_FOUND


class BadRequestError(ApplicationError):
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST


class ForbiddenError(ApplicationError):
    status_code: HTTPStatus = HTTPStatus.FORBIDDEN


class UnauthorizedError(ApplicationError):
    status_code: HTTPStatus = HTTPStatus.UNAUTHORIZED


# TODO: вынести инициализацию `detail` в родительский класс, использовать родительский класс
class NotValidValueError(ApplicationError):
    """Исключение для невалидных данных."""

    def __init__(self, detail: str | None) -> None:
        self.detail = detail
        super().__init__()


# TODO: в коде, для получения `object_name` используется: `self._model.__name__`, `Shift.__doc__`
#       `Shift.__name__`, `Report.__name__` — **необходимо привести к единому формату**
# TODO: Заменить `object_name` на сам объект, посмотреть, можно ли брать `object_id` из объекта
class ObjectNotFoundError(NotFoundError):
    def __init__(self, object_name: str, object_id: UUID):
        self.detail = "Объект {} с id: {} не найден".format(object_name, object_id)


class ObjectAlreadyExistsError(BadRequestError):
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


# TODO: Заменить `shift_name` и `shift_id` на сам объект, `Shift`
class ShiftStartError(BadRequestError):
    def __init__(self, shift_name: str, shift_id: UUID):
        self.detail = f"Невозможно начать смену {shift_name} с id: {shift_id}. Проверьте статус смены"


class ShiftReadyForCompleteForbiddenException(BadRequestError):
    def __init__(self, shift_name: str, shift_id: UUID):
        self.detail = (
            f"Невозможно перевести в статус 'завершающаяся' смену {shift_name} с id: {shift_id}. Проверьте статус смены"
        )


# TODO: Заменить `shift_name` и `shift_id` на сам объект, `Shift`
class ShiftFinishError(BadRequestError):
    def __init__(self, shift_name: str, shift_id: UUID):
        self.detail = f"Невозможно завершить смену {shift_name} с id: {shift_id}. Проверьте статус смены"


# TODO: Заменить `shift_name` и `shift_id` на сам объект, `Shift`
# TODO: вынести инициализацию `detail` в родительский класс — ???
class ShiftCancelError(BadRequestError):
    def __init__(self, shift_name: str, shift_id: UUID):
        self.detail = f"Невозможно отменить смену {shift_name} с id: {shift_id}. Проверьте статус смены"


# TODO: вынести инициализацию `detail` в родительский класс, использовать родительский класс — ???
class CreateShiftForbiddenError(ForbiddenError):
    def __init__(self, detail: str):
        self.detail = detail


# TODO: вынести инициализацию `detail` в родительский класс, использовать родительский класс — ???
class ShiftUpdateError(BadRequestError):
    def __init__(self, detail: str):
        self.detail = detail


# TODO: вынести инициализацию `detail` в родительский класс, использовать родительский класс — ???
class UpdateShiftForbiddenError(ForbiddenError):
    def __init__(self, detail: str):
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


# Todo: вынести адрес группы ВКонтакте в настройки
class RegistrationForbiddenError(ForbiddenError):
    detail = (
        "К сожалению, на данный момент мы не можем зарегистрировать вас в проекте: смена уже "
        "началась и группа участников набрана. Чтобы не пропустить актуальные новости "
        "Центра \"Ломая барьеры\" - вступайте в нашу группу ВКонтакте https://vk.com/socialrb02"
    )


# Todo: вынести адрес группы ВКонтакте в настройки
class AlreadyRegisteredError(ForbiddenError):
    detail = (
        "Вы уже зарегистрированы в проекте, ожидайте свое первое задание "
        "в день старта смены. Актуальную дату начала смены вы можете "
        "посмотреть в нашей группе ВКонтакте https://vk.com/socialrb02"
    )


class RequestAlreadyReviewedError(ForbiddenError):
    def __init__(self, status: Request.Status):
        self.detail = "Заявка на участие уже проверена, статус заявки: {}.".format(status)


# Todo: вынести адрес группы ВКонтакте в настройки
class RequestForbiddenError(ForbiddenError):
    detail = (
        "К сожалению, на данный момент мы не можем зарегистрировать вас на текущую смену. "
        "Чтобы не пропустить актуальные новости Центра \"Ломая барьеры\" - вступайте "
        "в нашу группу ВКонтакте https://vk.com/socialrb02"
    )


class InvalidAuthenticationDataError(ForbiddenError):
    """Введены неверные данные для аутентификации."""

    detail = "Неверный email или пароль."


class AdministratorBlockedError(ForbiddenError):
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


class InvitationAlreadyDeactivatedError(ForbiddenError):
    detail = "Приглашение уже деактивировано"


class InvitationAlreadyActivatedError(ForbiddenError):
    detail = "Приглашение активно"


class AdministratorChangeError(ForbiddenError):
    detail = "У вас нет прав на изменение других администраторов."


class AdministratorSelfChangeRoleError(ForbiddenError):
    detail = "Вы не можете изменить роль самому себе."


class AdministratorBlockError(ForbiddenError):
    detail = "У Вас нет прав на блокировку других администраторов."


class AdministratorSelfBlockError(ForbiddenError):
    detail = "Вы не можете заблокировать себя."
